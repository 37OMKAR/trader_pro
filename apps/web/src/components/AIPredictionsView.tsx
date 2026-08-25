"use client";

import React, { useState, useEffect } from "react";
import { Cpu, TrendingUp, TrendingDown, RefreshCw, Filter, Sparkles } from "lucide-react";
import { MarketAPI } from "@/lib/api";
import { formatNumber, formatPercent } from "@/lib/utils";

interface AIPredictionsViewProps {
  onSelectStock: (symbol: string) => void;
}

export function AIPredictionsView({ onSelectStock }: AIPredictionsViewProps) {
  const [predictions, setPredictions] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterHorizon, setFilterHorizon] = useState<string>("5D");

  const symbols = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "BHARTIARTL", "SBIN", "LT", "BAJFINANCE", "TATAMOTORS"];

  const loadPredictions = async () => {
    setLoading(true);
    try {
      const results = await Promise.all(
        symbols.map((sym) => MarketAPI.getStockPrediction(sym, filterHorizon))
      );
      setPredictions(results);
    } catch (err) {
      console.error("Error loading predictions:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPredictions();
  }, [filterHorizon]);

  return (
    <div className="space-y-5">
      {/* Header Bar */}
      <div className="terminal-card p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-cyan-400" />
            <h2 className="text-base font-bold font-mono text-white">AI MACHINE LEARNING PREDICTION REGISTRY</h2>
          </div>
          <div className="text-xs text-[#64748b] font-mono mt-0.5">
            Factor Ensemble & Gradient Boosted Multi-Horizon Directional Models (NSE Large-Cap Universe)
          </div>
        </div>

        <div className="flex items-center gap-3 font-mono text-xs">
          <div className="flex items-center bg-[#090d16] p-1 rounded border border-[#1e293b]">
            {["1D", "5D", "20D"].map((h) => (
              <button
                key={h}
                onClick={() => setFilterHorizon(h)}
                className={`px-3 py-1 rounded transition ${
                  filterHorizon === h
                    ? "bg-cyan-500 text-black font-bold"
                    : "text-[#64748b] hover:text-white"
                }`}
              >
                {h} Horizon
              </button>
            ))}
          </div>

          <button
            onClick={loadPredictions}
            className="p-2 rounded bg-[#151b2c] hover:bg-[#1e293b] text-[#94a3b8] hover:text-white border border-[#1e293b] transition"
            title="Recalculate Predictions"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-cyan-400" : ""}`} />
          </button>
        </div>
      </div>

      {/* Grid of Predictions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {predictions.map((pred) => {
          const isUp = pred.direction === "UP";
          return (
            <div
              key={pred.symbol}
              onClick={() => onSelectStock(pred.symbol)}
              className="terminal-card p-4 hover:border-cyan-500/50 cursor-pointer transition flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold font-mono text-white">{pred.symbol}</span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#151b2c] text-[#94a3b8]">
                      {pred.horizon}
                    </span>
                  </div>
                  <div
                    className={`px-2 py-0.5 rounded text-xs font-mono font-bold flex items-center gap-1 ${
                      isUp
                        ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                        : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                    }`}
                  >
                    {isUp ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                    <span>{pred.direction}</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 my-3 font-mono text-xs">
                  <div className="bg-[#090d16] p-2 rounded border border-[#1e293b]">
                    <div className="text-[10px] text-[#64748b]">Probability</div>
                    <div className="text-sm font-bold text-white mt-0.5">
                      {Math.round(pred.probability * 100)}%
                    </div>
                  </div>
                  <div className="bg-[#090d16] p-2 rounded border border-[#1e293b]">
                    <div className="text-[10px] text-[#64748b]">Exp. Return</div>
                    <div className="text-sm font-bold text-cyan-400 mt-0.5">
                      {pred.expected_return > 0 ? `+${pred.expected_return}%` : `${pred.expected_return}%`}
                    </div>
                  </div>
                </div>

                <div className="space-y-1 text-[11px] font-mono text-[#94a3b8]">
                  {pred.drivers?.slice(0, 2).map((d: string, i: number) => (
                    <div key={i} className="truncate text-[#64748b]">
                      • {d}
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-2 mt-3 border-t border-[#1e293b]/70 flex items-center justify-between text-[10px] font-mono text-[#64748b]">
                <span>Confidence: {Math.round(pred.confidence * 100)}%</span>
                <span className="text-cyan-400 hover:underline">View Deep Profile →</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
