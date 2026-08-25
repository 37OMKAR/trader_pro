"use client";

import React from "react";
import { SectorPerformance } from "@/types";
import { formatPercent } from "@/lib/utils";
import { PieChart } from "lucide-react";

interface SectorHeatmapProps {
  sectors: SectorPerformance[];
}

export function SectorHeatmap({ sectors }: SectorHeatmapProps) {
  return (
    <div className="terminal-card p-4">
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-[#1e293b]">
        <div className="flex items-center gap-2">
          <PieChart className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-bold text-white font-mono tracking-wide">
            SECTOR PERFORMANCE & HEATMAP
          </span>
        </div>
        <span className="text-[11px] font-mono text-[#64748b]">NIFTY Sectoral Indices</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-3 gap-2.5">
        {sectors.map((sec) => {
          const isUp = sec.percent_change >= 0;
          return (
            <div
              key={sec.sector_name}
              className={`p-2.5 rounded-lg border transition-all ${
                isUp
                  ? "bg-emerald-950/20 border-emerald-500/30 hover:border-emerald-500/50"
                  : "bg-rose-950/20 border-rose-500/30 hover:border-rose-500/50"
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold text-white font-mono truncate">{sec.sector_name}</span>
                <span
                  className={`text-xs font-mono font-bold ${
                    isUp ? "text-emerald-400" : "text-rose-400"
                  }`}
                >
                  {formatPercent(sec.percent_change)}
                </span>
              </div>
              <div className="flex items-center justify-between text-[10px] font-mono text-[#64748b]">
                <span>Top: <span className="text-[#94a3b8]">{sec.top_contributor || "N/A"}</span></span>
                <span>Wt: {sec.weight_pct}%</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
