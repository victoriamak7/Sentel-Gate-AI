import json
import boto3
from typing import Dict, Any
from sentinel_gate.config import settings

class SNSAlertService:
    """
    Amazon SNS Real-Time Alerting Service.
    Dispatches immediate notifications to enterprise security operations (SOC)
    when critical credentials, private keys, or database passwords are intercepted.
    """

    def __init__(self):
        self.topic_arn = settings.SNS_ALERT_TOPIC_ARN
        self.region = settings.AWS_REGION
        self._sns_client = None
        self._init_client()

    def _init_client(self):
        if self.topic_arn:
            try:
                self._sns_client = boto3.client("sns", region_name=self.region)
            except Exception:
                self._sns_client = None

    def send_credential_leak_alert(self, user_id: str, matched_rule: str, snippet: str, session_id: str):
        if not self._sns_client or not self.topic_arn:
            return

        subject = f"[CRITICAL SECURITY ALERT] Confidential Credential Intercepted by Sentinel-Gate AI"
        message = (
            f"ALERT: Sentinel-Gate AI Policy Firewall intercepted a critical credential leak.\n\n"
            f"User ID: {user_id}\n"
            f"Session ID: {session_id}\n"
            f"Violation Rule: {matched_rule}\n"
            f"Snippet Preview: {snippet}\n"
            f"Action Taken: External LLM dispatch was DETERMINISTICALLY HALTED.\n"
            f"Policy Reference: Enterprise Data Handling Standard §4.2\n"
        )

        try:
            self._sns_client.publish(
                TopicArn=self.topic_arn,
                Subject=subject[:100],
                Message=message
            )
        except Exception:
            pass

sns_alert_service = SNSAlertService()
