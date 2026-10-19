from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import time
import uuid

class PolicyCategory(str, Enum):
    PUBLIC_SAFE = "PUBLIC_SAFE"
    SENSITIVE_PII = "SENSITIVE_PII"
    CONFIDENTIAL_BLOCKED = "CONFIDENTIAL_BLOCKED"
    UNCERTAIN_REVIEW = "UNCERTAIN_REVIEW"

class PolicyEnforcementAction(str, Enum):
    PASS_THROUGH = "PASS_THROUGH"
    REDACT_AND_FORWARD = "REDACT_AND_FORWARD"
    BLOCK_IMMEDIATE = "BLOCK_IMMEDIATE"
    HOLD_FOR_REVIEW = "HOLD_FOR_REVIEW"

class TypedPolicyQuestion(BaseModel):
    """
    Typed question schema for Strands Decider 2B enterprise policy evaluation.
    """
    question: str = Field(
        default="Does this input comply with Enterprise Data Security and Privacy Classification Policies?",
        description="The typed governance query evaluated by Decider 2B."
    )
    options: List[str] = Field(
        default=[
            "PUBLIC_SAFE: General knowledge, code templates, or sanitized content.",
            "SENSITIVE_PII: Personal identifying information (emails, phone numbers, SSNs).",
            "CONFIDENTIAL_BLOCKED: Secret credentials, DB strings, API keys, or trade secrets.",
            "UNCERTAIN_REVIEW: Ambiguous input or confidence below strict safety threshold."
        ],
        description="Discrete action choices for deterministic policy gatekeeping."
    )
    strict_mode: bool = Field(default=True)

class FirewallEvaluationRequest(BaseModel):
    prompt: str = Field(..., description="Employee prompt or code snippet submitted to the enterprise portal")
    user_id: Optional[str] = Field(default="emp_anonymous", description="Employee identifier or departmental role")
    session_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    bypass_cache: bool = Field(default=False)
    allow_redaction: bool = Field(default=True)

class RedactionMetadata(BaseModel):
    total_redactions: int = 0
    redacted_items: List[Dict[str, str]] = []
    sanitized_text: str = ""

class BedrockRemediation(BaseModel):
    memo_title: str
    explanation: str
    policy_citation: str
    suggested_safe_alternative: str
    sanitized_mock_query: str
    generated_by: str = "Amazon Bedrock (Automated Policy Remediation)"

class PolicyDecision(BaseModel):
    id: str = Field(default_factory=lambda: f"dec_{uuid.uuid4().hex[:12]}")
    timestamp: float = Field(default_factory=time.time)
    category: PolicyCategory
    action: PolicyEnforcementAction
    confidence_score: float
    decider_latency_ms: float
    matched_rules: List[str] = []
    redaction: Optional[RedactionMetadata] = None
    bedrock_invoked: bool = False
    bedrock_latency_ms: float = 0.0
    bedrock_response: Optional[str] = None
    bedrock_remediation: Optional[BedrockRemediation] = None
    estimated_tokens_saved: int = 0
    estimated_cost_saved_usd: float = 0.0
    cache_hit: bool = False
    audit_logged: bool = True

class ChatProxyRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: Optional[str] = "anthropic.claude-3-haiku-20240307-v1:0"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024

class TelemetrySnapshot(BaseModel):
    total_requests: int
    blocked_count: int
    pii_redacted_count: int
    passed_safe_count: int
    uncertain_review_count: int
    avg_decider_latency_ms: float
    total_tokens_saved: int
    total_cost_saved_usd: float
    cache_hit_rate: float
    last_updated: float
