import os
from pydantic import BaseModel, Field

class SentinelConfig(BaseModel):
    # Service Configuration
    ENVIRONMENT: str = Field(default_factory=lambda: os.getenv("SENTINEL_ENV", "development"))
    SERVICE_PORT: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    SERVICE_HOST: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    
    # Strands Decider 2B Settings
    DECIDER_MODEL_NAME: str = Field(default="strands-decider-2b")
    DECIDER_TARGET_LATENCY_MS: float = Field(default=115.0)
    CONFIDENCE_THRESHOLD: float = Field(default=0.85)
    FAIL_CLOSED_ON_UNCERTAIN: bool = Field(default=True)
    
    # Amazon Bedrock Settings
    AWS_REGION: str = Field(default_factory=lambda: os.getenv("AWS_DEFAULT_REGION", os.getenv("AWS_REGION", "us-east-1")))
    BEDROCK_MODEL_ID: str = Field(default_factory=lambda: os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0"))
    BEDROCK_REMEDIATION_MODEL_ID: str = Field(default_factory=lambda: os.getenv("BEDROCK_REMEDIATION_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0"))
    AWS_ACCESS_KEY_ID: str | None = Field(default_factory=lambda: os.getenv("AWS_ACCESS_KEY_ID"))
    AWS_SECRET_ACCESS_KEY: str | None = Field(default_factory=lambda: os.getenv("AWS_SECRET_ACCESS_KEY"))
    
    # CloudWatch Metrics
    CLOUDWATCH_NAMESPACE: str = Field(default="SentinelGate/PolicyFirewall")
    ENABLE_CLOUDWATCH: bool = Field(default_factory=lambda: os.getenv("ENABLE_CLOUDWATCH", "false").lower() == "true")
    
    # Optional Cloud Services
    DYNAMODB_TABLE_NAME: str = Field(default_factory=lambda: os.getenv("DYNAMODB_TABLE_NAME", "SentinelPolicyCache"))
    S3_AUDIT_BUCKET: str = Field(default_factory=lambda: os.getenv("S3_AUDIT_BUCKET", "sentinel-gate-audit-logs"))
    SNS_ALERT_TOPIC_ARN: str = Field(default_factory=lambda: os.getenv("SNS_ALERT_TOPIC_ARN", ""))

    # Cost calculation constants (per 1,000 tokens)
    COST_PER_1K_FRONTIER_INPUT: float = 0.003
    COST_PER_1K_FRONTIER_OUTPUT: float = 0.015
    COST_PER_1K_DECIDER_2B: float = 0.00000  # Local/edge model evaluation has 0 LLM token cost

settings = SentinelConfig()
