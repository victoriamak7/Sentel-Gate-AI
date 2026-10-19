import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentinel_gate.backend.routers import firewall, telemetry, benchmark

app = FastAPI(
    title="Sentinel-Gate AI",
    description="An AI Policy Firewall Agent for Enterprise Data Security & Compliance using Strands Decider 2B & Amazon Bedrock",
    version="1.0.0"
)

# Enable CORS for Next.js frontend and enterprise callers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(firewall.router, prefix="/api/v1")
app.include_router(telemetry.router, prefix="/api/v1")
app.include_router(benchmark.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "service": "Sentinel-Gate AI Policy Firewall",
        "tagline": "Inline AI Policy Gatekeeper in ~115ms",
        "technologies": [
            "Strands Decider 2B",
            "Strands Agents SDK",
            "Amazon Bedrock",
            "C++20 Zero-Copy Pattern Engine",
            "FastAPI",
            "Amazon CloudWatch",
            "Amazon DynamoDB",
            "Amazon S3",
            "Amazon SNS",
            "AWS IAM",
            "Docker",
            "Next.js"
        ],
        "endpoints": {
            "evaluate": "/api/v1/firewall/evaluate",
            "chat_proxy": "/api/v1/firewall/chat/completions",
            "metrics": "/api/v1/telemetry/metrics",
            "audit_logs": "/api/v1/telemetry/audit/logs",
            "benchmark": "/api/v1/benchmark/run",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run("sentinel_gate.backend.main:app", host="0.0.0.0", port=8000, reload=True)
