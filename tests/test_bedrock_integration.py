import pytest
from sentinel_gate.integrations.bedrock_service import bedrock_service

def test_bedrock_safe_prompt_response():
    prompt = "Explain binary search in 2 bullet points."
    res = bedrock_service.generate_safe_response(prompt)
    
    assert "text" in res
    assert len(res["text"]) > 10
    assert "latency_ms" in res

def test_bedrock_compliance_remediation_memo():
    memo = bedrock_service.generate_compliance_remediation(
        matched_rule="DB_CONNECTION_STRING",
        prompt_snippet="postgres://admin:secretPass@prod-db.internal:5432/users"
    )
    
    assert "Data Handling Standard §4.2" in memo.policy_citation
    assert "postgres" in memo.sanitized_mock_query
    assert "$DB_PASSWORD" in memo.sanitized_mock_query
