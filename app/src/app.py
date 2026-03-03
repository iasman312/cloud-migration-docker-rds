import os
import time
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "notesdb")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")


def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def init_db(retries=20, delay=1):
    last_err = None
    for _ in range(retries):
        try:
            conn = get_conn()
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS notes (
                        id SERIAL PRIMARY KEY,
                        content TEXT NOT NULL
                    );
                """)
            conn.close()
            print("DB init: notes table is ready")
            return
        except Exception as e:
            last_err = e
            print(f"DB init: waiting for DB... ({e})")
            time.sleep(delay)
    raise RuntimeError(f"DB init failed after retries: {last_err}")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/notes")
def list_notes():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT id, content FROM notes ORDER BY id DESC;")
        rows = cur.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "content": r[1]} for r in rows])


@app.post("/notes")
def create_note():
    data = request.get_json(force=True) or {}
    content = (data.get("content") or "").strip()
    if not content:
        return {"error": "content is required"}, 400

    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("INSERT INTO notes (content) VALUES (%s) RETURNING id;", (content,))
        new_id = cur.fetchone()[0]
        conn.commit()
    conn.close()
    return {"id": new_id, "content": content}, 201


if __name__ == "__main__":
    init_db()
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)