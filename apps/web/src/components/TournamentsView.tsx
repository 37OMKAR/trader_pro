"use client";

import React, { useState, useEffect } from "react";
import { Trophy, Award, TrendingUp, Shield, BarChart3, RefreshCw, Zap, Star } from "lucide-react";
import { MarketAPI } from "@/lib/api";
import { formatNumber, formatPercent } from "@/lib/utils";

export function TournamentsView() {
  const [asset, setAsset] = useState<string>("RELIANCE");
  const [tournamentData, setTournamentData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const loadTournament = async (targetAsset: string) => {
    setLoading(true);
    try {
      const data = await MarketAPI.getTournamentLeaderboard(targetAsset);
      setTournamentData(data);
    } catch (err) {
      console.error("Error loading tournament:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTournament(asset);
  }, [asset]);

  const getBadgeColor = (badge: string) => {
    switch (badge) {
      case "ELITE_ALPHA":
        return "bg-amber-500/15 text-amber-400 border-amber-500/30";
      case "BALANCED_ALL_WEATHER":
        return "bg-cyan-500/15 text-cyan-400 border-cyan-500/30";
      case "HIGH_MOMENTUM":
        return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
      default:
        return "bg-slate-500/15 text-slate-400 border-slate-500/30";
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="terminal-card p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Trophy className="w-5 h-5 text-amber-400" />
            <h2 className="text-base font-bold font-mono text-white">
              STRATEGY TOURNAMENT LEADERBOARD
            </h2>
          </div>
          <div className="text-xs text-[#64748b] font-mono mt-0.5">
            Head-to-Head Quantitative Model Tournaments & Multi-Factor StrategyScore Rankings
          </div>
        </div>

        <div className="flex items-center gap-3 font-mono text-xs">
          <div className="flex items-center gap-2">
            <span className="text-[#64748b]">Tournament Asset:</span>
            <select
              value={asset}
              onChange={(e) => setAsset(e.target.value)}
              className="bg-[#090d16] border border-[#1e293b] rounded px-3 py-1.5 text-white font-mono"
            >
              {["RELIANCE", "TCS", "HDFCBANK", "INFY", "TATAMOTORS", "NIFTY 50"].map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          <button
            onClick={() => loadTournament(asset)}
            className="p-2 rounded bg-[#151b2c] hover:bg-[#1e293b] text-[#94a3b8] hover:text-white border border-[#1e293b] transition"
            title="Re-run Tournament"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-cyan-400" : ""}`} />
          </button>
        </div>
      </div>

      {/* Leaderboard Cards */}
      <div className="space-y-4 font-mono">
        {loading ? (
          <div className="terminal-card p-12 text-center text-xs text-cyan-400 animate-pulse">
            Simulating Head-to-Head Strategy Tournament on {asset}...
          </div>
        ) : (
          tournamentData?.leaderboard?.map((entry: any) => {
            const isFirst = entry.rank === 1;
            return (
              <div
                key={entry.strategy_id}
                className={`terminal-card p-5 transition ${
                  isFirst
                    ? "border-amber-500/50 bg-gradient-to-r from-[#0d1322] via-[#101728] to-[#151924]"
                    : "hover:border-[#334155]"
                }`}
              >
                <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-8 h-8 rounded-lg font-bold flex items-center justify-center text-sm ${
                        isFirst
                          ? "bg-amber-400 text-black shadow-glow-amber"
                          : entry.rank === 2
                          ? "bg-slate-300 text-black"
                          : entry.rank === 3
                          ? "bg-amber-700 text-white"
                          : "bg-[#151b2c] text-[#94a3b8]"
                      }`}
                    >
                      #{entry.rank}
                    </div>

                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-white">{entry.name}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded border font-semibold ${getBadgeColor(entry.badge)}`}>
                          {entry.badge}
                        </span>
                      </div>
                      <div className="text-xs text-[#64748b] mt-0.5">{entry.description}</div>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-2xl font-bold text-cyan-400">
                      {entry.strategy_score}
                      <span className="text-xs text-[#64748b] font-normal"> / 100</span>
                    </div>
                    <div className="text-[10px] text-[#64748b] uppercase">{entry.tier}</div>
                  </div>
                </div>

                {/* KPI Statistics */}
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs mb-3">
                  <div className="bg-[#090d16] p-2.5 rounded border border-[#1e293b]">
                    <div className="text-[10px] text-[#64748b]">Total Return</div>
                    <div className={`text-sm font-bold mt-0.5 ${entry.metrics.total_return_pct >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                      {entry.metrics.total_return_pct >= 0 ? `+${entry.metrics.total_return_pct}%` : `${entry.metrics.total_return_pct}%`}
                    </div>
                  </div>

                  <div className="bg-[#090d16] p-2.5 rounded border border-[#1e293b]">
                    <div className="text-[10px] text-[#64748b]">Sharpe Ratio</div>
                    <div className="text-sm font-bold text-cyan-400 mt-0.5">
                      {entry.metrics.sharpe_ratio}
                    </div>
                  </div>

                  <div className="bg-[#090d16] p-2.5 rounded border border-[#1e293b]">
                    <div className="text-[10px] text-[#64748b]">Max Drawdown</div>
                    <div className="text-sm font-bold text-rose-400 mt-0.5">
                      -{entry.metrics.max_drawdown_pct}%
                    </div>
                  </div>

                  <div className="bg-[#090d16] p-2.5 rounded border border-[#1e293b]">
                    <div className="text-[10px] text-[#64748b]">Win Rate</div>
                    <div className="text-sm font-bold text-white mt-0.5">
                      {entry.metrics.win_rate_pct}%
                    </div>
                  </div>

                  <div className="bg-[#090d16] p-2.5 rounded border border-[#1e293b]">
                    <div className="text-[10px] text-[#64748b]">Profit Factor</div>
                    <div className="text-sm font-bold text-emerald-400 mt-0.5">
                      {entry.metrics.profit_factor}x
                    </div>
                  </div>
                </div>

                {/* Sub-Score Breakdown Bars */}
                <div className="pt-2 border-t border-[#1e293b]/70 grid grid-cols-5 gap-2 text-[10px] text-[#64748b]">
                  <div>Return: <span className="text-white font-semibold">{entry.sub_scores.return_score}</span></div>
                  <div>Sharpe: <span className="text-white font-semibold">{entry.sub_scores.sharpe_score}</span></div>
                  <div>Drawdown: <span className="text-white font-semibold">{entry.sub_scores.drawdown_score}</span></div>
                  <div>Stability: <span className="text-white font-semibold">{entry.sub_scores.stability_score}</span></div>
                  <div>Robustness: <span className="text-white font-semibold">{entry.sub_scores.robustness_score}</span></div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
