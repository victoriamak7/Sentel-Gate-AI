from fastapi import APIRouter
from sentinel_gate.integrations.cloudwatch_service import cloudwatch_service
from sentinel_gate.integrations.s3_audit import s3_audit_service
from sentinel_gate.integrations.dynamodb_cache import dynamodb_cache
from sentinel_gate.integrations.bedrock_service import bedrock_service

router = APIRouter(prefix="/telemetry", tags=["Telemetry & Audit"])

@router.get("/metrics")
async def get_metrics():
    """
    Returns real-time aggregated metrics:
    - Decider 2B latency distribution
    - Total tokens and dollars saved
    - Category breakdown (Blocked vs Redacted vs Safe vs Uncertain)
    - DynamoDB cache hit rate
    """
    snapshot = cloudwatch_service.get_telemetry_snapshot()
    snapshot["dynamodb_cache_hit_rate"] = dynamodb_cache.get_hit_rate()
    snapshot["bedrock_live_status"] = bedrock_service.is_live()
    return snapshot

@router.get("/audit/logs")
async def get_audit_logs(limit: int = 50):
    """
    Returns recent compliance audit entries.
    """
    return {
        "count": len(s3_audit_service.get_recent_audit_logs(limit)),
        "logs": s3_audit_service.get_recent_audit_logs(limit)
    }

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Sentinel-Gate AI Policy Firewall",
        "version": "1.0.0",
        "decider_model": "strands-decider-2b",
        "remediation_backend": "Amazon Bedrock"
    }
