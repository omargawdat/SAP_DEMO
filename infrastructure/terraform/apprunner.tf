# Data source for AWS account ID
data "aws_caller_identity" "current" {}

# App Runner Service for FastAPI
resource "aws_apprunner_service" "api" {
  service_name = "${var.project_name}-api"

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_ecr.arn
    }

    image_repository {
      image_identifier      = "${aws_ecr_repository.api.repository_url}:latest"
      image_repository_type = "ECR"

      image_configuration {
        port = "8000"

        runtime_environment_secrets = {
          ANTHROPIC_API_KEY = "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:${var.project_name}/anthropic-api-key"
        }

        runtime_environment_variables = {
          PYTHONUNBUFFERED = "1"
        }
      }
    }

    auto_deployments_enabled = true
  }

  instance_configuration {
    cpu               = "512"
    memory            = "1024"
    instance_role_arn = aws_iam_role.apprunner_instance.arn
  }

  health_check_configuration {
    protocol            = "HTTP"
    path                = "/api/v1/health"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 1
    unhealthy_threshold = 5
  }

  tags = {
    Name        = "${var.project_name}-api"
    Environment = var.environment
  }
}
