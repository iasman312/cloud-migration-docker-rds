output "rds_endpoint" {
  description = "RDS database endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_address" {
  description = "RDS database address (without port)"
  value       = aws_db_instance.postgres.address
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_task_definition" {
  description = "ECS task definition family"
  value       = aws_ecs_task_definition.app.family
}

output "ecs_task_definition_arn" {
  description = "ECS task definition ARN"
  value       = aws_ecs_task_definition.app.arn
}

output "ec2_instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.ecs_instance.id
}

output "ec2_public_ip" {
  description = "EC2 instance public IP (Elastic IP)"
  value       = aws_eip.ecs_instance.public_ip
}

output "application_url" {
  description = "Application URL"
  value       = "http://${aws_eip.ecs_instance.public_ip}:${var.container_port}"
}

output "security_group_ec2" {
  description = "Security group ID for EC2 instance"
  value       = aws_security_group.ec2_instance.id
}

output "docker_login_command" {
  description = "Command to login to ECR"
  value       = "aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.app.repository_url}"
  sensitive   = false
}