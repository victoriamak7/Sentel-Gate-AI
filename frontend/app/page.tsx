"use client";

import React, { useState, useEffect } from "react";
import { Header } from "../components/Header";
import { TelemetryGauges } from "../components/TelemetryGauges";
import { PromptWorkbench } from "../components/PromptWorkbench";
import { BenchmarkVisualizer } from "../components/BenchmarkVisualizer";
import { AuditLogTable } from "../components/AuditLogTable";

export default function Home() {
  const [metrics, setMetrics] = useState({
    total_requests: 0,
    blocked_count: 0,
    pii_redacted_count: 0,
    passed_safe_count: 0,
    uncertain_review_count: 0,
    avg_decider_latency_ms: 114.8,
    total_tokens_saved: 0,
    total_cost_saved_usd: 0.0,
    dynamodb_cache_hit_rate: 0
  });

  const [refreshKey, setRefreshKey] = useState<number>(0);

  const fetchMetrics = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/telemetry/metrics");
      if (res.ok) {
        const json = await res.json();
        setMetrics(json);
      }
    } catch {
      // Backend may be initializing
    }
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleEvaluationCompleted = () => {
    fetchMetrics();
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="min-h-screen bg-sentinel-dark flex flex-col font-sans">
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
        {/* Real-time KPI Telemetry */}
        <TelemetryGauges metrics={metrics} />

        {/* Interactive Prompt & Policy Inspection Workbench */}
        <PromptWorkbench onEvaluationCompleted={handleEvaluationCompleted} />

        {/* Decider 2B vs Bedrock Benchmark Suite */}
        <BenchmarkVisualizer />

        {/* Compliance Audit Log */}
        <AuditLogTable refreshTrigger={refreshKey} />
      </main>

      <footer className="border-t border-gray-800 py-6 text-center text-xs text-gray-500">
        <p>Sentinel-Gate AI &bull; Built with Strands Decider 2B, Strands Agents SDK & Amazon Bedrock</p>
        <p className="mt-1">Tags: <span className="text-gray-400">#strands-decider-2b</span> &bull; <span className="text-gray-400">#policy</span></p>
      </footer>
    </div>
  );
}
