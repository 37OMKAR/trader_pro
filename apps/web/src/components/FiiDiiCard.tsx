"use client";

import React from "react";
import { FiiDiiActivity } from "@/types";
import { formatINR } from "@/lib/utils";
import { Building2, ArrowUpRight, ArrowDownRight } from "lucide-react";

interface FiiDiiCardProps {
  fiiDii: FiiDiiActivity | null;
}

export function FiiDiiCard({ fiiDii }: FiiDiiCardProps) {
  if (!fiiDii) return null;

  const isFiiNetBuy = fiiDii.fii_net >= 0;
  const isDiiNetBuy = fiiDii.dii_net >= 0;
  const isTotalNetBuy = fiiDii.total_institutional_net >= 0;

  return (
    <div className="terminal-card p-4 flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-[#1e293b]">
        <div className="flex items-center gap-2">
          <Building2 className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-bold text-white font-mono tracking-wide">FII / DII ACTIVITY</span>
        </div>
        <span
          className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
            isTotalNetBuy ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
          }`}
        >
          Net: {formatINR(fiiDii.total_institutional_net, true)}
        </span>
      </div>

      {/* Breakdown */}
      <div className="grid grid-cols-2 gap-3 mb-2 font-mono">
        {/* FII Column */}
        <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
          <div className="text-[11px] font-bold text-white mb-1.5 flex items-center justify-between">
            <span>FII (Foreign)</span>
            {isFiiNetBuy ? (
              <ArrowUpRight className="w-3.5 h-3.5 text-emerald-400" />
            ) : (
              <ArrowDownRight className="w-3.5 h-3.5 text-rose-400" />
            )}
          </div>
          <div className="text-xs space-y-1">
            <div className="text-[#64748b] flex justify-between">
              <span>Buy:</span> <span className="text-[#94a3b8]">{formatINR(fiiDii.fii_buy_gross, true)}</span>
            </div>
            <div className="text-[#64748b] flex justify-between">
              <span>Sell:</span> <span className="text-[#94a3b8]">{formatINR(fiiDii.fii_sell_gross, true)}</span>
            </div>
            <div className="pt-1 border-t border-[#1e293b] flex justify-between font-bold">
              <span>Net:</span>
              <span className={isFiiNetBuy ? "text-emerald-400" : "text-rose-400"}>
                {formatINR(fiiDii.fii_net, true)}
              </span>
            </div>
          </div>
        </div>

        {/* DII Column */}
        <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
          <div className="text-[11px] font-bold text-white mb-1.5 flex items-center justify-between">
            <span>DII (Domestic)</span>
            {isDiiNetBuy ? (
              <ArrowUpRight className="w-3.5 h-3.5 text-emerald-400" />
            ) : (
              <ArrowDownRight className="w-3.5 h-3.5 text-rose-400" />
            )}
          </div>
          <div className="text-xs space-y-1">
            <div className="text-[#64748b] flex justify-between">
              <span>Buy:</span> <span className="text-[#94a3b8]">{formatINR(fiiDii.dii_buy_gross, true)}</span>
            </div>
            <div className="text-[#64748b] flex justify-between">
              <span>Sell:</span> <span className="text-[#94a3b8]">{formatINR(fiiDii.dii_sell_gross, true)}</span>
            </div>
            <div className="pt-1 border-t border-[#1e293b] flex justify-between font-bold">
              <span>Net:</span>
              <span className={isDiiNetBuy ? "text-emerald-400" : "text-rose-400"}>
                {formatINR(fiiDii.dii_net, true)}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="text-[10px] font-mono text-[#64748b] text-right">
        Cash Market Figures (₹ in Crores)
      </div>
    </div>
  );
}
