import re
from typing import Tuple, Dict, List
from sentinel_gate.core.models import RedactionMetadata

class LocalRedactionUtility:
    """
    Local redaction engine that masks PII and sensitive user metadata
    before forwarding safe portions to Amazon Bedrock.
    Ensures PII never crosses external network boundaries.
    """
    
    EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    PHONE_REGEX = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
    SSN_REGEX = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
    CREDIT_CARD_REGEX = re.compile(r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b')
    IP_ADDRESS_REGEX = re.compile(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b')

    def redact(self, text: str) -> Tuple[str, RedactionMetadata]:
        sanitized = text
        redacted_items: List[Dict[str, str]] = []
        counter = 1

        # 1. Redact Emails
        for match in self.EMAIL_REGEX.finditer(text):
            val = match.group(0)
            token = f"[REDACTED_EMAIL_{counter}]"
            sanitized = sanitized.replace(val, token)
            redacted_items.append({"type": "EMAIL", "original_snippet": val[:3] + "***@" + val.split("@")[-1], "token": token})
            counter += 1

        # 2. Redact Phone Numbers
        for match in self.PHONE_REGEX.finditer(text):
            val = match.group(0)
            token = f"[REDACTED_PHONE_{counter}]"
            sanitized = sanitized.replace(val, token)
            redacted_items.append({"type": "PHONE", "original_snippet": "***-***-" + val[-4:], "token": token})
            counter += 1

        # 3. Redact SSN
        for match in self.SSN_REGEX.finditer(text):
            val = match.group(0)
            token = f"[REDACTED_SSN_{counter}]"
            sanitized = sanitized.replace(val, token)
            redacted_items.append({"type": "SSN", "original_snippet": "***-**-" + val[-4:], "token": token})
            counter += 1

        # 4. Redact Credit Cards
        for match in self.CREDIT_CARD_REGEX.finditer(text):
            val = match.group(0)
            token = f"[REDACTED_CARD_{counter}]"
            sanitized = sanitized.replace(val, token)
            redacted_items.append({"type": "CREDIT_CARD", "original_snippet": "****-****-****-" + val[-4:], "token": token})
            counter += 1

        metadata = RedactionMetadata(
            total_redactions=len(redacted_items),
            redacted_items=redacted_items,
            sanitized_text=sanitized
        )

        return sanitized, metadata

redaction_engine = LocalRedactionUtility()
