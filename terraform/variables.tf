variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region for deployment"
}

variable "environment" {
  type        = string
  default     = "prod"
  description = "Deployment environment (dev, staging, prod)"
}

variable "aws_account_id" {
  type        = string
  default     = "123456789012"
  description = "AWS Account ID used for unique S3 bucket naming"
}
