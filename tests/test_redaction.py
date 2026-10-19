import pytest
from sentinel_gate.core.redaction import redaction_engine

def test_email_and_phone_redaction():
    text = "Contact Jane Doe at jane.doe@acme.corp or call +1-800-555-0199 for billing."
    sanitized, metadata = redaction_engine.redact(text)
    
    assert "[REDACTED_EMAIL_1]" in sanitized
    assert "jane.doe@acme.corp" not in sanitized
    assert "[REDACTED_PHONE_2]" in sanitized
    assert "+1-800-555-0199" not in sanitized
    assert metadata.total_redactions == 2

def test_ssn_redaction():
    text = "Verification: SSN 123-45-6789 verified."
    sanitized, metadata = redaction_engine.redact(text)
    
    assert "[REDACTED_SSN_1]" in sanitized
    assert "123-45-6789" not in sanitized
    assert metadata.total_redactions == 1
