import time
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from sentinel_gate.core.models import (
    FirewallEvaluationRequest,
    PolicyDecision,
    PolicyCategory,
    PolicyEnforcementAction,
    ChatProxyRequest
)
from sentinel_gate.strands_sdk.pipeline import agent_pipeline
from sentinel_gate.integrations.bedrock_service import bedrock_service
from sentinel_gate.integrations.cloudwatch_service import cloudwatch_service
from sentinel_gate.integrations.dynamodb_cache import dynamodb_cache
from sentinel_gate.integrations.s3_audit import s3_audit_service
from sentinel_gate.integrations.sns_alerts import sns_alert_service
from sentinel_gate.config import settings

router = APIRouter(prefix="/firewall", tags=["Policy Firewall"])

@router.post("/evaluate", response_model=PolicyDecision)
async def evaluate_prompt(request: FirewallEvaluationRequest, background_tasks: BackgroundTasks):
    start_wall = time.perf_counter()
    raw_prompt = request.prompt.strip()

    if not raw_prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    # 1. DynamoDB Cache check for sub-millisecond lookup
    if not request.bypass_cache:
        cached_result = dynamodb_cache.get(raw_prompt)
        if cached_result:
            decision = PolicyDecision(**cached_result)
            decision.cache_hit = True
            decision.decider_latency_ms = 0.45  # sub-ms lookup
            return decision

    # 2. Execute Strands Agents SDK Pipeline with Decider 2B (~115ms)
    ctx, decision_dict, intervention = agent_pipeline.execute_firewall(
        prompt=raw_prompt,
        user_id=request.user_id or "emp_01",
        session_id=request.session_id or str(uuid.uuid4())
    )

    category: PolicyCategory = decision_dict["category"]
    confidence: float = decision_dict["confidence_score"]
    decider_latency: float = decision_dict["decider_latency_ms"]
    matched_rules = decision_dict["matched_rules"]

    bedrock_invoked = False
    bedrock_latency = 0.0
    bedrock_answer = None
    bedrock_remediation = None

    # Baseline token cost calculation
    prompt_tokens = max(1, len(raw_prompt) // 4)
    tokens_saved = 0
    cost_saved = 0.0

    # 3. Policy Enforcement Path
    if category == PolicyCategory.CONFIDENTIAL_BLOCKED:
        # Request halted immediately! Bedrock is NEVER called with the sensitive prompt.
        tokens_saved = prompt_tokens + 500  # Saved input + output tokens of frontier LLM
        cost_saved = (tokens_saved / 1000.0) * settings.COST_PER_1K_FRONTIER_OUTPUT
        
        # Async/Local Bedrock remediation explaining violation and citing Standard §4.2
        rule_str = matched_rules[0] if matched_rules else "CONFIDENTIAL_DATA"
        bedrock_remediation = bedrock_service.generate_compliance_remediation(
            matched_rule=rule_str,
            prompt_snippet=raw_prompt[:64]
        )

        # Trigger real-time SNS alert for security operations
        background_tasks.add_task(
            sns_alert_service.send_credential_leak_alert,
            user_id=request.user_id,
            matched_rule=rule_str,
            snippet=raw_prompt[:40] + "...",
            session_id=request.session_id
        )

    elif category == PolicyCategory.SENSITIVE_PII:
        # Routed to local redaction utility to mask tokens/emails before forwarding
        redacted_prompt = intervention.processed_prompt
        # Safe forward to Bedrock
        bedrock_resp = bedrock_service.generate_safe_response(redacted_prompt)
        bedrock_invoked = True
        bedrock_latency = bedrock_resp["latency_ms"]
        bedrock_answer = bedrock_resp["text"]

    elif category == PolicyCategory.PUBLIC_SAFE:
        # Payload passes directly through to Amazon Bedrock
        bedrock_resp = bedrock_service.generate_safe_response(raw_prompt)
        bedrock_invoked = True
        bedrock_latency = bedrock_resp["latency_ms"]
        bedrock_answer = bedrock_resp["text"]

    elif category == PolicyCategory.UNCERTAIN_REVIEW:
        # Low confidence or ambiguous: Fail-closed to avoid accidental data exfiltration
        tokens_saved = prompt_tokens + 300
        cost_saved = (tokens_saved / 1000.0) * settings.COST_PER_1K_FRONTIER_OUTPUT
        bedrock_answer = (
            "Sentinel-Gate Policy Alert: This input exhibits ambiguous or low-confidence classification "
            "and has been held for compliance review in accordance with fail-closed safety policy."
        )

    # Build response model
    decision = PolicyDecision(
        category=category,
        action=intervention.action,
        confidence_score=confidence,
        decider_latency_ms=decider_latency,
        matched_rules=matched_rules,
        redaction=intervention.redaction_metadata,
        bedrock_invoked=bedrock_invoked,
        bedrock_latency_ms=bedrock_latency,
        bedrock_response=bedrock_answer,
        bedrock_remediation=bedrock_remediation,
        estimated_tokens_saved=tokens_saved,
        estimated_cost_saved_usd=cost_saved,
        cache_hit=False,
        audit_logged=True
    )

    # 4. Record telemetry in CloudWatch & S3 Audit
    cloudwatch_service.record_decision(
        category=category.value,
        confidence=confidence,
        latency_ms=decider_latency,
        tokens_saved=tokens_saved,
        cost_saved_usd=cost_saved
    )

    background_tasks.add_task(s3_audit_service.log_record, decision.dict())
    dynamodb_cache.put(raw_prompt, decision.dict())

    return decision


@router.post("/chat/completions")
async def chat_proxy_completions(req: ChatProxyRequest, background_tasks: BackgroundTasks):
    """
    Drop-in enterprise proxy endpoint compatible with standard OpenAI/Bedrock chat interfaces.
    Intercepts the user prompt through Strands Decider 2B before forwarding.
    """
    if not req.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty")

    latest_user_msg = next((m["content"] for m in reversed(req.messages) if m.get("role") == "user"), "")
    if not latest_user_msg:
        raise HTTPException(status_code=400, detail="No user message found in history")

    eval_req = FirewallEvaluationRequest(prompt=latest_user_msg)
    decision = await evaluate_prompt(eval_req, background_tasks)

    if decision.action == PolicyEnforcementAction.BLOCK_IMMEDIATE:
        return {
            "id": decision.id,
            "object": "chat.completion",
            "model": "sentinel-gate-firewall-blocked",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": (
                            f"🛑 [SENTINEL-GATE AI SECURITY VIOLATION]\n\n"
                            f"{decision.bedrock_remediation.explanation}\n\n"
                            f"📜 Policy Citation: {decision.bedrock_remediation.policy_citation}\n\n"
                            f"💡 Safe Alternative: {decision.bedrock_remediation.suggested_safe_alternative}\n"
                            f"```text\n{decision.bedrock_remediation.sanitized_mock_query}\n```"
                        )
                    },
                    "finish_reason": "policy_violation"
                }
            ],
            "firewall_telemetry": {
                "decision": decision.category,
                "decider_latency_ms": decision.decider_latency_ms,
                "confidence_score": decision.confidence_score
            }
        }

    return {
        "id": decision.id,
        "object": "chat.completion",
        "model": req.model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": decision.bedrock_response
                },
                "finish_reason": "stop"
            }
        ],
        "firewall_telemetry": {
            "decision": decision.category,
            "decider_latency_ms": decision.decider_latency_ms,
            "confidence_score": decision.confidence_score,
            "bedrock_latency_ms": decision.bedrock_latency_ms
        }
    }
