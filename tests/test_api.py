import pytest
from fastapi.testclient import TestClient
from sentinel_gate.backend.main import app

client = TestClient(app)

def test_api_health():
    res = client.get("/api/v1/telemetry/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_api_evaluate_confidential_blocked():
    payload = {
        "prompt": "Here is our production connection string: postgres://admin:secretPass@prod-db.internal:5432/users - write a script to migrate table X.",
        "user_id": "test_emp",
        "bypass_cache": True
    }
    res = client.post("/api/v1/firewall/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["category"] == "CONFIDENTIAL_BLOCKED"
    assert data["action"] == "BLOCK_IMMEDIATE"
    assert data["bedrock_invoked"] is False
    assert data["bedrock_remediation"] is not None
    assert "Data Handling Standard §4.2" in data["bedrock_remediation"]["policy_citation"]

def test_api_evaluate_pii():
    payload = {
        "prompt": "Email invoice to billing@client.com or call 555-010-9988",
        "bypass_cache": True
    }
    res = client.post("/api/v1/firewall/evaluate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["category"] == "SENSITIVE_PII"
    assert data["action"] == "REDACT_AND_FORWARD"
    assert data["bedrock_invoked"] is True
    assert data["redaction"]["total_redactions"] == 2

def test_api_benchmark_run():
    res = client.post("/api/v1/benchmark/run")
    assert res.status_code == 200
    data = res.json()
    assert "decider_2b_avg_latency_ms" in data
    assert "latency_reduction_percent" in data
    assert data["latency_reduction_percent"] > 80.0
