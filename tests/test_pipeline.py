import pytest
from sentinel_gate.strands_sdk.pipeline import agent_pipeline
from sentinel_gate.core.models import PolicyCategory, PolicyEnforcementAction

def test_pipeline_execution_confidential_block():
    prompt = "DATABASE_URL=postgres://root:p@ssword@internal.company:5432/app"
    ctx, decision, intervention = agent_pipeline.execute_firewall(prompt)
    
    assert decision["category"] == PolicyCategory.CONFIDENTIAL_BLOCKED
    assert intervention.allowed_to_dispatch_bedrock is False
    assert intervention.action == PolicyEnforcementAction.BLOCK_IMMEDIATE

def test_pipeline_execution_pii_redaction():
    prompt = "Please send invoice to john.smith@company.com"
    ctx, decision, intervention = agent_pipeline.execute_firewall(prompt)
    
    assert decision["category"] == PolicyCategory.SENSITIVE_PII
    assert intervention.allowed_to_dispatch_bedrock is True
    assert "[REDACTED_EMAIL_1]" in intervention.processed_prompt
