import pytest
from sentinel_gate.core.decider_2b import decider_2b_agent
from sentinel_gate.core.models import PolicyCategory, PolicyEnforcementAction

def test_confidential_db_string_blocked():
    prompt = "Here is our production connection string: postgres://admin:secretPass@prod-db.internal:5432/users - write a script to migrate table X."
    decision = decider_2b_agent.evaluate(prompt)
    
    assert decision["category"] == PolicyCategory.CONFIDENTIAL_BLOCKED
    assert decision["action"] == PolicyEnforcementAction.BLOCK_IMMEDIATE
    assert decision["confidence_score"] >= 0.85
    assert 100.0 <= decision["decider_latency_ms"] <= 140.0

def test_confidential_aws_keys_blocked():
    prompt = "Export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE and AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    decision = decider_2b_agent.evaluate(prompt)
    
    assert decision["category"] == PolicyCategory.CONFIDENTIAL_BLOCKED
    assert decision["action"] == PolicyEnforcementAction.BLOCK_IMMEDIATE

def test_sensitive_pii_redact_action():
    prompt = "Send email confirmation to customer support at alice@example.com or call 555-019-2831."
    decision = decider_2b_agent.evaluate(prompt)
    
    assert decision["category"] == PolicyCategory.SENSITIVE_PII
    assert decision["action"] == PolicyEnforcementAction.REDACT_AND_FORWARD

def test_public_safe_algorithm():
    prompt = "Implement merge sort in Python with clear comments and tests."
    decision = decider_2b_agent.evaluate(prompt)
    
    assert decision["category"] == PolicyCategory.PUBLIC_SAFE
    assert decision["action"] == PolicyEnforcementAction.PASS_THROUGH

def test_uncertain_review_fail_closed():
    prompt = "key"  # Ambiguous short input
    decision = decider_2b_agent.evaluate(prompt)
    
    assert decision["category"] == PolicyCategory.UNCERTAIN_REVIEW
    assert decision["action"] == PolicyEnforcementAction.HOLD_FOR_REVIEW
