import json
import time
from typing import Dict, Any, List
from collections import deque
import boto3
from sentinel_gate.config import settings

class S3AuditLogger:
    """
    Amazon S3 Audit Logging Service.
    Stores historical records of blocked compliance queries, PII redactions,
    and decision telemetry for enterprise compliance review (GDPR, SOC2, HIPAA).
    """

    def __init__(self):
        self.bucket_name = settings.S3_AUDIT_BUCKET
        self.region = settings.AWS_REGION
        self._s3_client = None
        self._audit_log_buffer: deque = deque(maxlen=500)
        self._init_client()

    def _init_client(self):
        try:
            self._s3_client = boto3.client("s3", region_name=self.region)
        except Exception:
            self._s3_client = None

    def log_record(self, record: Dict[str, Any]):
        record["logged_at"] = time.time()
        self._audit_log_buffer.append(record)

        # If S3 client is configured, flush record to S3 object key
        if self._s3_client and record.get("category") == "CONFIDENTIAL_BLOCKED":
            try:
                key = f"violations/{time.strftime('%Y/%m/%d')}/{record.get('id', 'unknown')}.json"
                self._s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=json.dumps(record, indent=2).encode("utf-8"),
                    ContentType="application/json"
                )
            except Exception:
                pass

    def get_recent_audit_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return list(self._audit_log_buffer)[-limit:]

s3_audit_service = S3AuditLogger()
