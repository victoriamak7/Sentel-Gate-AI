#!/usr/bin/env bash
# Sentinel-Gate AI: Benchmark Execution Script
# Validates Strands Decider 2B ~115ms decision loop vs Frontier LLM Direct Triage

set -e

echo "================================================================="
echo " Sentinel-Gate AI Benchmark & Latency Verification Suite"
echo " Evaluating Strands Decider 2B vs Frontier Generative LLM Triage"
echo "================================================================="

# Check Python environment
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed."
    exit 1
fi

echo "[1/3] Running automated unit and integration tests..."
python3 -m pytest tests/ -v

echo ""
echo "[2/3] Executing standalone latency & token profiling..."
python3 benchmarks/run_benchmarks.py

echo ""
echo "[3/3] Checking API benchmark endpoint (if running on :8000)..."
if curl -s http://localhost:8000/api/v1/telemetry/health > /dev/null; then
    echo "API is live. Running benchmark against endpoint..."
    curl -X POST http://localhost:8000/api/v1/benchmark/run | python3 -m json.tool
else
    echo "API server not currently running on :8000. Skipping live HTTP test."
fi

echo ""
echo "================================================================="
echo " Benchmark Complete. Results logged."
echo "================================================================="
