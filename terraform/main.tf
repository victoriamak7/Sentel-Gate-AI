terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# 1. IAM Role for Sentinel-Gate AI
resource "aws_iam_role" "sentinel_role" {
  name = "sentinel-gate-agent-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = ["ecs-tasks.amazonaws.com", "ec2.amazonaws.com"]
        }
      }
    ]
  })

  tags = {
    Project     = "Sentinel-Gate-AI"
    Environment = var.environment
  }
}

# 2. IAM Policy (Least-Privilege)
resource "aws_iam_policy" "sentinel_policy" {
  name        = "sentinel-gate-policy-${var.environment}"
  description = "Least-privilege policy for Amazon Bedrock and telemetry"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "BedrockInvocation"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = "*"
      },
      {
        Sid    = "CloudWatchMetrics"
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData"
        ]
        Resource = "*"
      },
      {
        Sid    = "DynamoDBCache"
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Resource = aws_dynamodb_table.policy_cache.arn
      },
      {
        Sid    = "S3AuditLogs"
        Effect = "Allow"
        Action = [
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.audit_logs.arn}/*"
      },
      {
        Sid    = "SNSSecurityAlerts"
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.security_alerts.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sentinel_attach" {
  role       = aws_iam_role.sentinel_role.name
  policy_arn = aws_iam_policy.sentinel_policy.arn
}

# 3. DynamoDB Decision Cache
resource "aws_dynamodb_table" "policy_cache" {
  name         = "SentinelPolicyCache-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "prompt_hash"

  attribute {
    name = "prompt_hash"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Project     = "Sentinel-Gate-AI"
    Environment = var.environment
  }
}

# 4. S3 Audit Log Bucket
resource "aws_s3_bucket" "audit_logs" {
  bucket        = "sentinel-gate-audit-logs-${var.environment}-${var.aws_account_id}"
  force_destroy = false

  tags = {
    Project     = "Sentinel-Gate-AI"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "audit_encryption" {
  bucket = aws_s3_bucket.audit_logs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "audit_block_public" {
  bucket = aws_s3_bucket.audit_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 5. SNS Alert Topic
resource "aws_sns_topic" "security_alerts" {
  name         = "SentinelGate-SecurityAlerts-${var.environment}"
  display_name = "Sentinel-Gate AI Security Alerts"
}
