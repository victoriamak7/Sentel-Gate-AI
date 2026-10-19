"use client";

import React from "react";
import { ShieldCheck, Cpu, Cloud, Zap, Lock } from "lucide-react";

export const Header: React.FC = () => {
  return (
    <header className="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-50 px-6 py-4">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600/20 text-blue-400 rounded-lg border border-blue-500/30">
              <ShieldCheck className="w-7 h-7 text-blue-400 animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                SENTINEL-GATE AI
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  #strands-decider-2b
                </span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 border border-purple-500/30">
                  #policy
                </span>
              </h1>
              <p className="text-sm text-gray-400">
                AI Policy Firewall Agent for Enterprise Data Security & Compliance
              </p>
            </div>
          </div>
        </div>

        {/* Status badges showing integrated technologies */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-950/60 text-emerald-400 border border-emerald-800">
            <Zap className="w-3.5 h-3.5" />
            <span>Decider 2B (~115ms)</span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-950/60 text-amber-400 border border-amber-800">
            <Cloud className="w-3.5 h-3.5" />
            <span>Amazon Bedrock</span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-cyan-950/60 text-cyan-400 border border-cyan-800">
            <Cpu className="w-3.5 h-3.5" />
            <span>C++20 Zero-Copy</span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-blue-950/60 text-blue-400 border border-blue-800">
            <Lock className="w-3.5 h-3.5" />
            <span>Zero-Trust Enforced</span>
          </div>
        </div>
      </div>
    </header>
  );
};
