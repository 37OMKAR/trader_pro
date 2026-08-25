"use client";

import React from "react";
import { Quote } from "@/types";
import { formatINR, formatNumber, formatPercent } from "@/lib/utils";
import { ArrowUpRight, ArrowDownRight, Layers } from "lucide-react";

interface TopMoversTableProps {
  stocks: Quote[];
  onSelectStock: (symbol: string) => void;
}

export function TopMoversTable({ stocks, onSelectStock }: TopMoversTableProps) {
  const sorted = [...stocks].sort((a, b) => b.percent_change - a.percent_change);
  const gainers = sorted.slice(0, 5);
  const losers = sorted.slice(-5).reverse();

  return (
    <div className="terminal-card p-4">
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-[#1e293b]">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-bold text-white font-mono tracking-wide">
            TOP MARKET MOVERS (NIFTY LARGE-CAP)
          </span>
        </div>
        <span className="text-[11px] font-mono text-[#64748b]">Live Quotes</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Top Gainers */}
        <div>
          <div className="text-[11px] font-mono font-bold text-emerald-400 mb-2 flex items-center gap-1">
            <ArrowUpRight className="w-3.5 h-3.5" /> TOP GAINERS
          </div>
          <div className="space-y-1">
            {gainers.map((stk) => (
              <div
                key={stk.symbol}
                onClick={() => onSelectStock(stk.symbol)}
                className="flex items-center justify-between p-2 rounded bg-[#090d16] hover:bg-[#151b2c] cursor-pointer border border-[#1e293b] font-mono text-xs transition"
              >
                <div>
                  <span className="font-bold text-white">{stk.symbol}</span>
                  <div className="text-[10px] text-[#64748b] truncate max-w-[120px]">{stk.company_name}</div>
                </div>
                <div className="text-right">
                  <div className="text-white font-bold">{formatINR(stk.last_price)}</div>
                  <div className="text-emerald-400 font-semibold">{formatPercent(stk.percent_change)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Losers */}
        <div>
          <div className="text-[11px] font-mono font-bold text-rose-400 mb-2 flex items-center gap-1">
            <ArrowDownRight className="w-3.5 h-3.5" /> TOP LOSERS
          </div>
          <div className="space-y-1">
            {losers.map((stk) => (
              <div
                key={stk.symbol}
                onClick={() => onSelectStock(stk.symbol)}
                className="flex items-center justify-between p-2 rounded bg-[#090d16] hover:bg-[#151b2c] cursor-pointer border border-[#1e293b] font-mono text-xs transition"
              >
                <div>
                  <span className="font-bold text-white">{stk.symbol}</span>
                  <div className="text-[10px] text-[#64748b] truncate max-w-[120px]">{stk.company_name}</div>
                </div>
                <div className="text-right">
                  <div className="text-white font-bold">{formatINR(stk.last_price)}</div>
                  <div className="text-rose-400 font-semibold">{formatPercent(stk.percent_change)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
