"use client";

import React, { useState } from "react";
import { 
  Play, 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  EyeOff, 
  Copy, 
  Check, 
  FileText, 
  Sparkles, 
  Clock, 
  Coins 
} from "lucide-react";

interface DecisionResponse {
  id: string;
  category: "PUBLIC_SAFE" | "SENSITIVE_PII" | "CONFIDENTIAL_BLOCKED" | "UNCERTAIN_REVIEW";
  action: string;
  confidence_score: number;
  decider_latency_ms: number;
  matched_rules: string[];
  redaction?: {
    total_redactions: number;
    redacted_items: Array<{ type: string; original_snippet: string; token: string }>;
    sanitized_text: string;
  };
  bedrock_invoked: boolean;
  bedrock_latency_ms: number;
  bedrock_response?: string;
  bedrock_remediation?: {
    memo_title: string;
    explanation: string;
    policy_citation: string;
    suggested_safe_alternative: string;
    sanitized_mock_query: string;
    generated_by: string;
  };
  estimated_tokens_saved: number;
  estimated_cost_saved_usd: number;
}

const SAMPLE_PAYLOADS = [
  {
    label: "🚨 Production DB Secret (PDF Scenario)",
    category: "CONFIDENTIAL_BLOCKED",
    prompt: "Here is our production connection string: postgres://admin:secretPass@prod-db.internal:5432/users - write a script to migrate table X."
  },
  {
    label: "🔑 AWS Root Keys Leak",
    category: "CONFIDENTIAL_BLOCKED",
    prompt: "Export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE and AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY. How do I sync S3?"
  },
  {
    label: "👤 Customer PII (Email & Phone)",
    category: "SENSITIVE_PII",
    prompt: "Customer query from Alice Smith (alice.smith@enterprise-client.com, +1-555-839-2910): Please write an automated renewal acknowledgement email."
  },
  {
    label: "✅ Safe Code Query",
    category: "PUBLIC_SAFE",
    prompt: "Write a high-performance thread-safe LRU cache implementation in Python with type annotations and docstrings."
  },
  {
    label: "⚠️ Ambiguous Payload",
    category: "UNCERTAIN_REVIEW",
    prompt: "internal pass"
  }
];

export const PromptWorkbench: React.FC<{ onEvaluationCompleted: () => void }> = ({ onEvaluationCompleted }) => {
  const [prompt, setPrompt] = useState<string>(SAMPLE_PAYLOADS[0].prompt);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<DecisionResponse | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  const handleEvaluate = async (targetPrompt?: string) => {
    const textToTest = targetPrompt || prompt;
    if (!textToTest.trim()) return;

    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/firewall/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: textToTest,
          user_id: "demo_developer_01",
          bypass_cache: false
        })
      });

      if (!res.ok) throw new Error("Evaluation failed");
      const data: DecisionResponse = await res.json();
      setResult(data);
      onEvaluationCompleted();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getCategoryBadge = (cat: string) => {
    switch (cat) {
      case "CONFIDENTIAL_BLOCKED":
        return {
          bg: "bg-rose-500/10 text-rose-400 border-rose-500/30",
          icon: ShieldAlert,
          label: "CONFIDENTIAL_BLOCKED — External LLM Aborted"
        };
      case "SENSITIVE_PII":
        return {
          bg: "bg-amber-500/10 text-amber-400 border-amber-500/30",
          icon: EyeOff,
          label: "SENSITIVE_PII — Redacted Locally & Forwarded"
        };
      case "PUBLIC_SAFE":
        return {
          bg: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
          icon: ShieldCheck,
          label: "PUBLIC_SAFE — Direct Pass-Through"
        };
      case "UNCERTAIN_REVIEW":
        return {
          bg: "bg-purple-500/10 text-purple-400 border-purple-500/30",
          icon: AlertTriangle,
          label: "UNCERTAIN_REVIEW — Fail-Closed Safety Hold"
        };
      default:
        return { bg: "bg-gray-800 text-gray-400 border-gray-700", icon: ShieldCheck, label: cat };
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-xl mb-8">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between pb-4 border-b border-gray-800 gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-400" />
            Interactive Policy Firewall Workbench
          </h2>
          <p className="text-xs text-gray-400">
            Submit employee prompts or test synthetic enterprise security vectors. Evaluated in ~115ms by Strands Decider 2B.
          </p>
        </div>

        {/* Quick-test Presets */}
        <div className="flex flex-wrap gap-2">
          {SAMPLE_PAYLOADS.map((sample, idx) => (
            <button
              key={idx}
              onClick={() => {
                setPrompt(sample.prompt);
                handleEvaluate(sample.prompt);
              }}
              className="px-2.5 py-1 text-xs rounded-md bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 transition"
            >
              {sample.label}
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <div className="mt-4">
        <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
          Employee Prompt / Code Snippet Input
        </label>
        <div className="relative">
          <textarea
            rows={4}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Paste code snippet, database query, or prompt here..."
            className="w-full bg-gray-950 border border-gray-800 rounded-lg p-3 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-500 font-mono"
          />
        </div>

        <div className="mt-3 flex items-center justify-between">
          <span className="text-xs text-gray-500">
            Press &quot;Evaluate with Sentinel-Gate&quot; to test the ~115ms inline policy loop.
          </span>
          <button
            onClick={() => handleEvaluate()}
            disabled={loading || !prompt.trim()}
            className="px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium text-sm flex items-center gap-2 shadow-lg shadow-blue-600/20 transition"
          >
            {loading ? (
              <span className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
            ) : (
              <Play className="w-4 h-4 fill-current" />
            )}
            Evaluate with Sentinel-Gate
          </button>
        </div>
      </div>

      {/* Evaluation Results */}
      {result && (
        <div className="mt-6 border-t border-gray-800 pt-6 animate-fadeIn">
          {/* Decision Pill Banner */}
          {(() => {
            const badge = getCategoryBadge(result.category);
            const Icon = badge.icon;
            return (
              <div className={`p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${badge.bg}`}>
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-black/20">
                    <Icon className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold tracking-tight">{badge.label}</h3>
                    <p className="text-xs opacity-90">
                      Confidence: {(result.confidence_score * 100).toFixed(1)}% | Policy Rule: {result.matched_rules.join(", ") || "STANDARD_CHECK"}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-4 text-xs font-mono">
                  <div className="flex items-center gap-1.5 bg-black/30 px-3 py-1.5 rounded-lg">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Decider: {result.decider_latency_ms}ms</span>
                  </div>

                  {result.estimated_tokens_saved > 0 && (
                    <div className="flex items-center gap-1.5 bg-emerald-900/40 text-emerald-300 px-3 py-1.5 rounded-lg border border-emerald-700/40">
                      <Coins className="w-3.5 h-3.5" />
                      <span>Saved ${result.estimated_cost_saved_usd.toFixed(4)}</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })()}

          {/* SENSITIVE_PII: Redaction Comparison */}
          {result.category === "SENSITIVE_PII" && result.redaction && (
            <div className="mt-4 p-4 rounded-xl bg-gray-950 border border-gray-800">
              <h4 className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-2 flex items-center gap-2">
                <EyeOff className="w-4 h-4" />
                Local Redaction Utility Output (Masked Before LLM Forwarding)
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="text-gray-500 block mb-1">Raw Input Payload:</span>
                  <div className="p-3 bg-gray-900 rounded-lg text-gray-300 font-mono break-all border border-gray-800">
                    {prompt}
                  </div>
                </div>
                <div>
                  <span className="text-gray-500 block mb-1">Sanitized Forwarded Payload:</span>
                  <div className="p-3 bg-gray-900 rounded-lg text-amber-300 font-mono break-all border border-amber-900/30">
                    {result.redaction.sanitized_text}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* CONFIDENTIAL_BLOCKED: Bedrock Compliance Remediation Memo */}
          {result.category === "CONFIDENTIAL_BLOCKED" && result.bedrock_remediation && (
            <div className="mt-4 p-5 rounded-xl bg-rose-950/20 border border-rose-900/40 text-gray-200">
              <div className="flex items-center justify-between pb-3 border-b border-rose-900/30">
                <h4 className="text-sm font-bold text-rose-400 flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  {result.bedrock_remediation.memo_title}
                </h4>
                <span className="text-xs px-2 py-0.5 rounded bg-rose-900/40 text-rose-300 border border-rose-700/50">
                  {result.bedrock_remediation.policy_citation}
                </span>
              </div>

              <p className="text-xs text-gray-300 mt-3 leading-relaxed">
                {result.bedrock_remediation.explanation}
              </p>

              <div className="mt-4 bg-gray-950 p-3.5 rounded-lg border border-gray-800">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-semibold text-emerald-400">
                    💡 Safe Enterprise Alternative:
                  </span>
                  <button
                    onClick={() => copyToClipboard(result.bedrock_remediation!.sanitized_mock_query)}
                    className="text-xs text-gray-400 hover:text-white flex items-center gap-1"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    Copy Safe Query
                  </button>
                </div>
                <p className="text-xs text-gray-400 mb-2">
                  {result.bedrock_remediation.suggested_safe_alternative}
                </p>
                <pre className="text-xs text-gray-300 font-mono bg-gray-900 p-2.5 rounded border border-gray-800 overflow-x-auto">
                  {result.bedrock_remediation.sanitized_mock_query}
                </pre>
              </div>
            </div>
          )}

          {/* PUBLIC_SAFE or REDACTED: Bedrock LLM Response */}
          {result.bedrock_response && (
            <div className="mt-4 p-5 rounded-xl bg-gray-950 border border-gray-800">
              <div className="flex items-center justify-between pb-2 border-b border-gray-800 mb-3">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-blue-400 flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  Amazon Bedrock Generative Response
                </h4>
                <span className="text-xs text-gray-500 font-mono">
                  Latency: {result.bedrock_latency_ms}ms
                </span>
              </div>
              <div className="text-xs text-gray-300 leading-relaxed whitespace-pre-wrap font-sans">
                {result.bedrock_response}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
