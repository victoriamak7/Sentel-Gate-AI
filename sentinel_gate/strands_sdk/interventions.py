from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
from sentinel_gate.core.models import (
    PolicyCategory,
    PolicyEnforcementAction,
    RedactionMetadata,
    BedrockRemediation
)
from sentinel_gate.core.redaction import redaction_engine

class InterventionResult:
    def __init__(
        self,
        action: PolicyEnforcementAction,
        allowed_to_dispatch_bedrock: bool,
        processed_prompt: str,
        redaction_metadata: Optional[RedactionMetadata] = None,
        reason: str = ""
    ):
        self.action = action
        self.allowed_to_dispatch_bedrock = allowed_to_dispatch_bedrock
        self.processed_prompt = processed_prompt
        self.redaction_metadata = redaction_metadata
        self.reason = reason


class BasePolicyIntervention(ABC):
    @abstractmethod
    def execute(self, prompt: str, decision: Dict[str, Any]) -> InterventionResult:
        pass


class BlockImmediateIntervention(BasePolicyIntervention):
    """
    Halts execution immediately. Amazon Bedrock is NEVER called with the confidential payload.
    """
    def execute(self, prompt: str, decision: Dict[str, Any]) -> InterventionResult:
        return InterventionResult(
            action=PolicyEnforcementAction.BLOCK_IMMEDIATE,
            allowed_to_dispatch_bedrock=False,
            processed_prompt="[PROMPT BLOCKED BY SENTINEL-GATE AI POLICY FIREWALL]",
            redaction_metadata=None,
            reason="Violation of Enterprise Data Handling Standard: Credentials/Secrets detected. External LLM dispatch aborted."
        )


class RedactAndForwardIntervention(BasePolicyIntervention):
    """
    Masks PII/tokens before forwarding safe text to Bedrock.
    """
    def execute(self, prompt: str, decision: Dict[str, Any]) -> InterventionResult:
        sanitized_text, metadata = redaction_engine.redact(prompt)
        return InterventionResult(
            action=PolicyEnforcementAction.REDACT_AND_FORWARD,
            allowed_to_dispatch_bedrock=True,
            processed_prompt=sanitized_text,
            redaction_metadata=metadata,
            reason=f"PII masked locally ({metadata.total_redactions} tokens redacted). Safe payload routed to Bedrock."
        )


class PassThroughIntervention(BasePolicyIntervention):
    """
    Passes directly through to Bedrock without modification.
    """
    def execute(self, prompt: str, decision: Dict[str, Any]) -> InterventionResult:
        return InterventionResult(
            action=PolicyEnforcementAction.PASS_THROUGH,
            allowed_to_dispatch_bedrock=True,
            processed_prompt=prompt,
            redaction_metadata=None,
            reason="Payload verified as PUBLIC_SAFE. Permitted for direct Bedrock inference."
        )


class HoldForReviewIntervention(BasePolicyIntervention):
    """
    Low confidence or ambiguous: Fail closed.
    """
    def execute(self, prompt: str, decision: Dict[str, Any]) -> InterventionResult:
        return InterventionResult(
            action=PolicyEnforcementAction.HOLD_FOR_REVIEW,
            allowed_to_dispatch_bedrock=False,
            processed_prompt="[PROMPT ON HOLD FOR COMPLIANCE REVIEW]",
            redaction_metadata=None,
            reason="Ambiguous or low-confidence classification. Enforcing fail-closed enterprise boundary."
        )
