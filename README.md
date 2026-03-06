# Cloud Migration: Docker & RDS

**Simple Flask Notes API with PostgreSQL RDS and ECS Deployment**

## Project Overview

This project demonstrates a cloud migration pattern for containerizing a Python Flask application and deploying it to AWS ECS with RDS PostgreSQL database.

## Architecture

```
Flask API (Docker) → ECS EC2 Instance → RDS PostgreSQL
```

**Components:**
- **Application**: Flask REST API for managing notes
- **Database**: AWS RDS PostgreSQL 15.17
- **Container**: Docker image stored in Amazon ECR
- **Orchestration**: AWS ECS on EC2 (t3.micro)
- **Infrastructure**: Terraform for IaC

## Project Structure

```
cloud-migration-docker-rds/
├── app/
│   ├── Dockerfile              # Container definition
│   ├── requirements.txt        # Python dependencies (Flask, psycopg2)
│   └── src/
│       └── app.py             # Flask application with notes CRUD API
├── terraform/
│   ├── provider.tf            # AWS provider configuration
│   ├── variables.tf           # Input variables
│   ├── ecr.tf                 # ECR repository for Docker images
│   ├── rds.tf                 # PostgreSQL RDS instance
│   ├── ecs.tf                 # ECS cluster, task definition, service
│   ├── security-groups.tf     # Network security rules
│   └── outputs.tf             # Output values (endpoints, IPs)
└── docker-compose.yaml        # Local development setup
```

## Application Details

### Flask API (`app/src/app.py`)

**Endpoints:**
- `GET /health` - Health check endpoint
- `GET /notes` - List all notes
- `POST /notes` - Create a new note

**Features:**
- PostgreSQL connection with retry logic
- Automatic table creation on startup
- Environment-based configuration
- CloudWatch logging integration

### Database Schema

```sql
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL
);
```

## Infrastructure Components

### 1. Amazon ECR (Elastic Container Registry)
- Repository: `cloud-migration-notesdb`
- Stores Docker images for deployment

### 2. Amazon RDS PostgreSQL
- **Engine**: PostgreSQL 15.17
- **Instance**: db.t3.micro
- **Storage**: 20 GB gp2
- **Access**: Publicly accessible (for demo purposes)
- **Backups**: Disabled (skip_final_snapshot: true)
- **Logs**: CloudWatch logs for postgresql and upgrades

### 3. Amazon ECS (Elastic Container Service)
- **Cluster**: `cloud-migration-notesdb-cluster`
- **Launch Type**: EC2 (t3.micro)
- **Container Insights**: Enabled
- **Network Mode**: Bridge
- **Memory**: 256 MB per task
- **Desired Count**: 1 task

### 4. EC2 Instance
- **AMI**: Amazon ECS-optimized AMI (Amazon Linux 2)
- **Instance Type**: t3.micro
- **Elastic IP**: Assigned for consistent access
- **Security Group**: Allows port 5000 (API) and 22 (SSH)

### 5. Security Groups
- **ECS EC2**: Allows inbound on port 5000 (API) and 22 (SSH)
- **RDS**: Allows inbound on port 5432 (PostgreSQL) from anywhere

### 6. CloudWatch Logs
- **Log Group**: `/ecs/cloud-migration-notesdb`
- **Retention**: 7 days
- **Stream Prefix**: `ecs`

## Environment Variables

The application uses the following environment variables (injected via ECS task definition):

```bash
DB_HOST=<rds-endpoint>
DB_PORT=5432
DB_NAME=notesdb
DB_USER=elenaadmin
DB_PASSWORD=<password>
```

## Deployment Workflow

1. **Build Docker Image**
   ```bash
   docker build -t notes-api:rds -f app/Dockerfile .
   ```

2. **Push to ECR**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker tag notes-api:rds <ecr-repo-url>:latest
   docker push <ecr-repo-url>:latest
   ```

3. **Deploy Infrastructure**
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

4. **ECS Service Deployment**
   - ECS automatically pulls the latest image from ECR
   - Creates task on EC2 instance
   - Connects to RDS PostgreSQL
   - Initializes database table on first run

## Local Development

Use Docker Compose for local testing:

```bash
docker-compose up
```

Access the API at: `http://localhost:5001`

**Note**: Update `DB_HOST` in `docker-compose.yaml` to point to your RDS instance.

## Testing the API

**Health Check:**
```bash
curl http://<ec2-public-ip>:5000/health
```

**Create Note:**
```bash
curl -X POST http://<ec2-public-ip>:5000/notes \
  -H "Content-Type: application/json" \
  -d '{"content": "My first note"}'
```

**List Notes:**
```bash
curl http://<ec2-public-ip>:5000/notes
```

## Terraform Outputs

After deployment, Terraform provides:
- `ecr_repository_url` - ECR repository URL
- `rds_endpoint` - PostgreSQL database endpoint
- `rds_port` - Database port (5432)
- `ecs_cluster_name` - ECS cluster name
- `ecs_service_name` - ECS service name
- `ec2_public_ip` - EC2 instance public IP
- `ec2_elastic_ip` - Elastic IP address

## Key Features

✅ **Containerization**: Flask app packaged in Docker  
✅ **Managed Database**: RDS PostgreSQL with automated backups  
✅ **Container Orchestration**: ECS for deployment and scaling  
✅ **Infrastructure as Code**: Terraform for reproducible deployments  
✅ **Logging**: CloudWatch Logs integration  
✅ **Monitoring**: ECS Container Insights enabled  
✅ **Persistent Storage**: RDS for data persistence  

## Cost Considerations

**Estimated Monthly Cost (us-east-1):**
- RDS db.t3.micro: ~$15/month
- EC2 t3.micro: ~$7.50/month
- Elastic IP: Free (when attached)
- ECR Storage: Minimal (<$1/month)
- CloudWatch Logs: Minimal (<$1/month)

**Total**: ~$25/month

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy
```

**Warning**: This will delete the RDS instance and all data.

## Security Notes

⚠️ **This is a demo/learning project** - Production deployments should:
- Use private subnets for RDS
- Restrict security group rules to specific CIDR blocks
- Enable RDS encryption at rest
- Use AWS Secrets Manager for database credentials
- Enable RDS automated backups
- Use IAM roles instead of hardcoded credentials
- Implement VPC endpoints for ECR access
- Enable SSL/TLS for database connections

## Technologies Used

- **Python 3.9** - Application runtime
- **Flask** - Web framework
- **psycopg2** - PostgreSQL adapter
- **Docker** - Containerization
- **Terraform** - Infrastructure as Code
- **AWS ECS** - Container orchestration
- **AWS RDS** - Managed PostgreSQL
- **AWS ECR** - Container registry
- **AWS CloudWatch** - Logging and monitoring

---

**Created**: March 5, 2026  
**Purpose**: Cloud migration learning project demonstrating Docker + RDS deployment on AWS ECS
