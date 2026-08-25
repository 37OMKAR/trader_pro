"use client";

import React from "react";
import { TrendingUp, TrendingDown, Activity } from "lucide-react";
import { IndexQuote } from "@/types";
import { formatNumber, formatPercent } from "@/lib/utils";

interface IndexSummaryCardsProps {
  indices: IndexQuote[];
  selectedSymbol: string;
  onSelectIndex: (symbol: string) => void;
}

export function IndexSummaryCards({ indices, selectedSymbol, onSelectIndex }: IndexSummaryCardsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {indices.slice(0, 4).map((idx) => {
        const isUp = idx.change >= 0;
        const isSelected = selectedSymbol === idx.symbol;

        return (
          <div
            key={idx.symbol}
            onClick={() => onSelectIndex(idx.symbol)}
            className={`terminal-card p-4 cursor-pointer relative overflow-hidden transition-all ${
              isSelected
                ? "border-cyan-500/50 bg-[#121929] shadow-glow-cyan/20"
                : "hover:border-[#334155]"
            }`}
          >
            {/* Header info */}
            <div className="flex items-center justify-between mb-2">
              <div>
                <span className="text-xs font-bold text-white tracking-wide">{idx.symbol}</span>
                <div className="text-[10px] text-[#64748b] truncate max-w-[120px]">{idx.name}</div>
              </div>
              <div
                className={`p-1.5 rounded text-xs font-mono font-semibold flex items-center gap-1 ${
                  isUp ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                }`}
              >
                {isUp ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                {formatPercent(idx.percent_change)}
              </div>
            </div>

            {/* Price Display */}
            <div className="flex items-baseline gap-2 mb-3">
              <span className="text-2xl font-bold font-mono text-white tracking-tight">
                {formatNumber(idx.current_value)}
              </span>
              <span
                className={`text-xs font-mono font-medium ${
                  isUp ? "text-emerald-400" : "text-rose-400"
                }`}
              >
                {isUp ? `+${formatNumber(idx.change)}` : formatNumber(idx.change)}
              </span>
            </div>

            {/* Day Range info */}
            <div className="pt-2 border-t border-[#1e293b]/70 flex items-center justify-between text-[11px] font-mono text-[#64748b]">
              <div>
                L: <span className="text-[#94a3b8]">{formatNumber(idx.low)}</span>
              </div>
              <div>
                H: <span className="text-[#94a3b8]">{formatNumber(idx.high)}</span>
              </div>
            </div>

            {/* Active accent bar */}
            {isSelected && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-400 to-emerald-400" />
            )}
          </div>
        );
      })}
    </div>
  );
}
