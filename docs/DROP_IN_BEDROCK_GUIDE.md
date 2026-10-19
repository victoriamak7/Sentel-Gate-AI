# Drop-in Integration Guide: Adding Sentinel-Gate Policy Firewall to Any Bedrock Agent

This guide shows how you can drop the **Sentinel-Gate AI Policy Firewall** into your existing Amazon Bedrock Python application or agent pipeline in under 5 lines of code.

---

## 1. Installation

```bash
pip install sentinel-gate-ai
```

Or copy the `sentinel_gate/` directory into your project.

---

## 2. Basic Drop-in Usage

Wrap your Amazon Bedrock invocation with `PolicyFirewallHandler`:

```python
from sentinel_gate.strands_sdk.handlers import PolicyFirewallHandler
from sentinel_gate.core.models import PolicyCategory
import boto3
import json

firewall = PolicyFirewallHandler()
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

def safe_bedrock_chat(user_prompt: str):
    # Step 1: Run inline Strands Decider 2B inspection (~115ms)
    decision, intervention = firewall.handle(user_prompt)

    # Step 2: Handle policy enforcement
    if decision["category"] == PolicyCategory.CONFIDENTIAL_BLOCKED:
        print("🛑 BLOCKED: Request contains credentials. Bedrock was NEVER called.")
        return {
            "status": "blocked",
            "message": "Prompt blocked by enterprise policy.",
            "latency_ms": decision["decider_latency_ms"]
        }

    # Step 3: Forward safe or redacted prompt to Amazon Bedrock
    payload = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": intervention.processed_prompt}]
    })

    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=payload
    )
    return json.loads(response["body"].read())
```

---

## 3. Bedrock Agent Action Group Hook

If you are using **AWS Bedrock Agents**, attach Sentinel-Gate as a Lambda Guardrail Pre-Processor:

```python
import json
from sentinel_gate.strands_sdk.handlers import PolicyFirewallHandler
from sentinel_gate.core.models import PolicyCategory

handler = PolicyFirewallHandler()

def lambda_handler(event, context):
    input_text = event.get("inputText", "")
    decision, intervention = handler.handle(input_text)

    if decision["category"] == PolicyCategory.CONFIDENTIAL_BLOCKED:
        return {
            "action": "DENY",
            "reason": f"Violated policy: {decision['matched_rules']}"
        }

    return {
        "action": "ALLOW",
        "sanitizedText": intervention.processed_prompt
    }
```

---

## 4. Drop-in OpenAI / LangChain Proxy

Sentinel-Gate AI exposes a standard `/api/v1/chat/completions` proxy. Point your existing client:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/api/v1/firewall",
    api_key="sentinel-proxy"
)

response = client.chat.completions.create(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    messages=[{"role": "user", "content": "How do I optimize SQL indexes?"}]
)
print(response.choices[0].message.content)
```
