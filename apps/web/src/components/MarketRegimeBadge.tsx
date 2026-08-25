"use client";

import React from "react";
import { MarketRegimeState } from "@/types";
import { ShieldCheck, AlertTriangle, Compass } from "lucide-react";

interface MarketRegimeBadgeProps {
  regime: MarketRegimeState | null;
}

export function MarketRegimeBadge({ regime }: MarketRegimeBadgeProps) {
  if (!regime) return null;

  const isBull = regime.regime === "BULL" || regime.regime === "RISK_ON";

  return (
    <div className="terminal-card p-4 flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-[#1e293b]">
        <div className="flex items-center gap-2">
          <Compass className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-bold text-white font-mono tracking-wide">
            AI MARKET REGIME
          </span>
        </div>
        <div className="flex items-center gap-2 font-mono">
          <span
            className={`text-xs font-bold px-2.5 py-0.5 rounded ${
              isBull
                ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
                : "bg-rose-500/20 text-rose-400 border border-rose-500/40"
            }`}
          >
            {regime.regime}
          </span>
        </div>
      </div>

      {/* Probabilities */}
      <div className="grid grid-cols-2 gap-2 mb-3 font-mono text-xs">
        <div className="bg-[#090d16] p-2 rounded border border-[#1e293b]">
          <span className="text-[#64748b]">Regime Prob: </span>
          <span className="text-white font-bold">{Math.round(regime.probability * 100)}%</span>
        </div>
        <div className="bg-[#090d16] p-2 rounded border border-[#1e293b]">
          <span className="text-[#64748b]">Confidence: </span>
          <span className="text-cyan-400 font-bold">{Math.round(regime.confidence * 100)}%</span>
        </div>
      </div>

      {/* Drivers List */}
      <div className="space-y-1.5 font-mono text-[11px]">
        <div className="text-[#64748b] text-[10px] uppercase font-bold tracking-wider">
          Primary Drivers:
        </div>
        {regime.drivers.slice(0, 3).map((driver, idx) => (
          <div key={idx} className="flex items-start gap-1.5 text-[#94a3b8]">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
            <span className="leading-tight">{driver}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
