"use client";

import React from "react";
import { MarketBreadth } from "@/types";
import { formatNumber } from "@/lib/utils";
import { Gauge, ArrowUpRight, ArrowDownRight } from "lucide-react";

interface MarketBreadthCardProps {
  breadth: MarketBreadth | null;
}

export function MarketBreadthCard({ breadth }: MarketBreadthCardProps) {
  if (!breadth) return null;

  const total = breadth.total_traded_stocks || 1;
  const advPct = Math.round((breadth.advances / total) * 100);
  const decPct = Math.round((breadth.declines / total) * 100);
  const unchPct = 100 - advPct - decPct;

  return (
    <div className="terminal-card p-4 flex flex-col justify-between">
      {/* Header */}
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-[#1e293b]">
        <div className="flex items-center gap-2">
          <Gauge className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-bold text-white font-mono tracking-wide">MARKET BREADTH</span>
        </div>
        <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
          ADR: {breadth.advance_decline_ratio}
        </span>
      </div>

      {/* Advance / Decline Bar */}
      <div className="space-y-2 mb-4">
        <div className="flex justify-between text-xs font-mono">
          <span className="text-emerald-400 font-semibold flex items-center gap-1">
            <ArrowUpRight className="w-3.5 h-3.5" /> Adv: {breadth.advances} ({advPct}%)
          </span>
          <span className="text-rose-400 font-semibold flex items-center gap-1">
            <ArrowDownRight className="w-3.5 h-3.5" /> Dec: {breadth.declines} ({decPct}%)
          </span>
        </div>

        {/* Visual Multi-Segment Bar */}
        <div className="w-full h-2.5 rounded-full bg-[#151b2c] overflow-hidden flex">
          <div style={{ width: `${advPct}%` }} className="bg-emerald-400 transition-all duration-500" />
          <div style={{ width: `${unchPct}%` }} className="bg-slate-500 transition-all duration-500" />
          <div style={{ width: `${decPct}%` }} className="bg-rose-400 transition-all duration-500" />
        </div>
      </div>

      {/* 52W High / Low & Circuits Stats */}
      <div className="grid grid-cols-2 gap-2 pt-3 border-t border-[#1e293b]/70 text-[11px] font-mono">
        <div className="bg-[#090d16] p-2 rounded border border-[#1e293b]">
          <span className="text-[#64748b]">52W Highs: </span>
          <span className="text-emerald-400 font-bold">{breadth.highs_52w}</span>
        </div>
        <div className="bg-[#090d16] p-2 rounded border border-[#1e293b]">
          <span className="text-[#64748b]">52W Lows: </span>
          <span className="text-rose-400 font-bold">{breadth.lows_52w}</span>
        </div>
        <div className="bg-[#090d16] p-2 rounded border border-[#1e293b]">
          <span className="text-[#64748b]">Upper Circuits: </span>
          <span className="text-emerald-400 font-bold">{breadth.upper_circuits}</span>
        </div>
        <div className="bg-[#090d16] p-2 rounded border border-[#1e293b]">
          <span className="text-[#64748b]">Lower Circuits: </span>
          <span className="text-rose-400 font-bold">{breadth.lower_circuits}</span>
        </div>
      </div>
    </div>
  );
}
