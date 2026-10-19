"use client";

import React, { useEffect, useState } from "react";
import { ScrollText, RefreshCw, CheckCircle, ShieldAlert, EyeOff } from "lucide-react";

interface AuditLog {
  id: string;
  category: string;
  confidence_score: number;
  decider_latency_ms: number;
  matched_rules: string[];
  estimated_cost_saved_usd: number;
  logged_at?: number;
}

export const AuditLogTable: React.FC<{ refreshTrigger: number }> = ({ refreshTrigger }) => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/telemetry/audit/logs?limit=15");
      if (res.ok) {
        const json = await res.json();
        setLogs(json.logs.reverse());
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [refreshTrigger]);

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-xl mb-12">
      <div className="flex items-center justify-between pb-4 border-b border-gray-800 mb-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <ScrollText className="w-5 h-5 text-gray-400" />
            Security & Compliance Audit Ledger
          </h2>
          <p className="text-xs text-gray-400">
            Real-time audit records stored for GDPR, SOC2, and HIPAA compliance verification.
          </p>
        </div>

        <button
          onClick={fetchLogs}
          disabled={loading}
          className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white transition"
          title="Refresh Logs"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border border-gray-800 rounded-lg overflow-hidden">
          <thead className="bg-gray-950 text-gray-400 border-b border-gray-800">
            <tr>
              <th className="p-3">Decision ID</th>
              <th className="p-3">Classification</th>
              <th className="p-3">Confidence</th>
              <th className="p-3">Latency</th>
              <th className="p-3">Violation Rule</th>
              <th className="p-3 text-right">Cost Saved</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-850 font-mono">
            {logs.length > 0 ? (
              logs.map((log, idx) => (
                <tr key={idx} className="hover:bg-gray-800/40">
                  <td className="p-3 text-gray-400">{log.id}</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                      log.category === "CONFIDENTIAL_BLOCKED" ? "bg-rose-500/20 text-rose-300" :
                      log.category === "SENSITIVE_PII" ? "bg-amber-500/20 text-amber-300" :
                      log.category === "UNCERTAIN_REVIEW" ? "bg-purple-500/20 text-purple-300" :
                      "bg-emerald-500/20 text-emerald-300"
                    }`}>
                      {log.category}
                    </span>
                  </td>
                  <td className="p-3 text-gray-300">{(log.confidence_score * 100).toFixed(1)}%</td>
                  <td className="p-3 text-blue-400">{log.decider_latency_ms}ms</td>
                  <td className="p-3 text-gray-400 font-sans text-xs">
                    {log.matched_rules?.length ? log.matched_rules.join(", ") : "PUBLIC_SAFE"}
                  </td>
                  <td className="p-3 text-right text-emerald-400">
                    ${log.estimated_cost_saved_usd.toFixed(4)}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={6} className="p-6 text-center text-gray-500 font-sans">
                  No audit logs recorded yet. Submit a prompt above or run the benchmark suite!
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
