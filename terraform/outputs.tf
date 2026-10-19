output "role_arn" {
  value       = aws_iam_role.sentinel_role.arn
  description = "IAM Execution Role ARN for Sentinel-Gate AI"
}

output "dynamodb_table_name" {
  value       = aws_dynamodb_table.policy_cache.name
  description = "DynamoDB cache table name"
}

output "s3_audit_bucket_name" {
  value       = aws_s3_bucket.audit_logs.id
  description = "S3 Audit Bucket name"
}

output "sns_alert_topic_arn" {
  value       = aws_sns_topic.security_alerts.arn
  description = "SNS Topic ARN for critical security alerts"
}
