# API URLs
output "api_url" {
  description = "FastAPI service URL"
  value       = "https://${aws_apprunner_service.api.service_url}"
}

output "api_docs_url" {
  description = "API documentation (Swagger UI)"
  value       = "https://${aws_apprunner_service.api.service_url}/api/v1/docs"
}

output "health_check_url" {
  description = "Health check endpoint"
  value       = "https://${aws_apprunner_service.api.service_url}/api/v1/health"
}

# ECR
output "ecr_api_url" {
  description = "ECR repository URL for API image"
  value       = aws_ecr_repository.api.repository_url
}

# AWS Info
output "aws_region" {
  description = "AWS region"
  value       = var.aws_region
}

output "aws_account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

# Helper commands
output "ecr_login_command" {
  description = "Command to login to ECR"
  value       = "aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com"
}

output "push_image_command" {
  description = "Command to push API image"
  value       = "docker push ${aws_ecr_repository.api.repository_url}:latest"
}
