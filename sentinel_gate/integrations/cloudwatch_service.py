import time
from typing import Dict, Any, List
from collections import deque
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from sentinel_gate.config import settings

class CloudWatchMetricsService:
    """
    Amazon CloudWatch metrics collector and telemetry manager for Sentinel-Gate AI.
    Emits latency, confidence scores, and policy classification execution metrics.
    """

    def __init__(self):
        self.namespace = settings.CLOUDWATCH_NAMESPACE
        self.region = settings.AWS_REGION
        self.enabled = settings.ENABLE_CLOUDWATCH
        self._cw_client = None
        self._init_client()

        # In-memory telemetry buffer for real-time dashboard visualization
        self.recent_events = deque(maxlen=200)
        self.total_requests = 0
        self.blocked_count = 0
        self.pii_redacted_count = 0
        self.passed_safe_count = 0
        self.uncertain_review_count = 0
        self.latencies: List[float] = []
        self.total_tokens_saved = 0
        self.total_cost_saved_usd = 0.0

    def _init_client(self):
        try:
            self._cw_client = boto3.client("cloudwatch", region_name=self.region)
        except Exception:
            self._cw_client = None

    def record_decision(
        self,
        category: str,
        confidence: float,
        latency_ms: float,
        tokens_saved: int,
        cost_saved_usd: float
    ):
        self.total_requests += 1
        self.latencies.append(latency_ms)
        self.total_tokens_saved += tokens_saved
        self.total_cost_saved_usd += cost_saved_usd

        if category == "CONFIDENTIAL_BLOCKED":
            self.blocked_count += 1
        elif category == "SENSITIVE_PII":
            self.pii_redacted_count += 1
        elif category == "PUBLIC_SAFE":
            self.passed_safe_count += 1
        elif category == "UNCERTAIN_REVIEW":
            self.uncertain_review_count += 1

        event = {
            "timestamp": time.time(),
            "category": category,
            "confidence": confidence,
            "latency_ms": latency_ms,
            "tokens_saved": tokens_saved,
            "cost_saved_usd": cost_saved_usd
        }
        self.recent_events.append(event)

        # Emit to AWS CloudWatch if enabled and client exists
        if self.enabled and self._cw_client:
            try:
                self._cw_client.put_metric_data(
                    Namespace=self.namespace,
                    MetricData=[
                        {
                            "MetricName": "DeciderLatency",
                            "Dimensions": [{"Name": "Category", "Value": category}],
                            "Value": latency_ms,
                            "Unit": "Milliseconds"
                        },
                        {
                            "MetricName": "ConfidenceScore",
                            "Dimensions": [{"Name": "Category", "Value": category}],
                            "Value": confidence * 100.0,
                            "Unit": "Percent"
                        },
                        {
                            "MetricName": "PolicyDecisionCount",
                            "Dimensions": [{"Name": "Category", "Value": category}],
                            "Value": 1,
                            "Unit": "Count"
                        },
                        {
                            "MetricName": "TokenCostSavedUSD",
                            "Dimensions": [{"Name": "Category", "Value": category}],
                            "Value": cost_saved_usd,
                            "Unit": "None"
                        }
                    ]
                )
            except Exception:
                pass

    def get_telemetry_snapshot(self) -> Dict[str, Any]:
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 115.0
        return {
            "total_requests": self.total_requests,
            "blocked_count": self.blocked_count,
            "pii_redacted_count": self.pii_redacted_count,
            "passed_safe_count": self.passed_safe_count,
            "uncertain_review_count": self.uncertain_review_count,
            "avg_decider_latency_ms": round(avg_latency, 2),
            "total_tokens_saved": self.total_tokens_saved,
            "total_cost_saved_usd": round(self.total_cost_saved_usd, 4),
            "cloudwatch_enabled": self.enabled,
            "cloudwatch_namespace": self.namespace,
            "recent_events": list(self.recent_events)[-25:]
        }

cloudwatch_service = CloudWatchMetricsService()
