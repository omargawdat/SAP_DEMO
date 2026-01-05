variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "pii-shield"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-central-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "demo"
}
