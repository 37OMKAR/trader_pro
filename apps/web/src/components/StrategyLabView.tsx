"use client";

import React, { useState, useEffect } from "react";
import { Play, Sparkles, Sliders, CheckCircle2, TrendingUp, TrendingDown, ArrowUpRight, BarChart2, Shield } from "lucide-react";
import { MarketAPI } from "@/lib/api";
import { formatINR, formatNumber, formatPercent } from "@/lib/utils";

export function StrategyLabView() {
  const [templates, setTemplates] = useState<any[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<any>(null);
  const [targetSymbol, setTargetSymbol] = useState<string>("RELIANCE");
  const [nlPrompt, setNlPrompt] = useState<string>("");
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [isBacktesting, setIsBacktesting] = useState<boolean>(false);
  const [backtestResult, setBacktestResult] = useState<any>(null);

  useEffect(() => {
    MarketAPI.getStrategyTemplates().then((tpls) => {
      setTemplates(tpls);
      if (tpls.length > 0) {
        setSelectedStrategy(tpls[0]);
      }
    }).catch(console.error);
  }, []);

  const handleGenerateNL = async () => {
    if (!nlPrompt.trim()) return;
    setIsGenerating(true);
    try {
      const generated = await MarketAPI.generateStrategyFromPrompt(nlPrompt);
      setSelectedStrategy(generated);
    } catch (err) {
      console.error("Error generating strategy:", err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRunBacktest = async () => {
    if (!selectedStrategy) return;
    setIsBacktesting(true);
    try {
      const res = await MarketAPI.runBacktest(selectedStrategy, targetSymbol, 1_000_000);
      setBacktestResult(res);
    } catch (err) {
      console.error("Error running backtest:", err);
    } finally {
      setIsBacktesting(false);
    }
  };

  const metrics = backtestResult?.metrics;

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="terminal-card p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Sliders className="w-5 h-5 text-cyan-400" />
            <h2 className="text-base font-bold font-mono text-white">
              QUANTITATIVE STRATEGY LAB & BACKTEST ENGINE
            </h2>
          </div>
          <div className="text-xs text-[#64748b] font-mono mt-0.5">
            Declarative Strategy DSL, AI Natural Language Creator & Realistic Indian Fee Backtesting
          </div>
        </div>

        <div className="flex items-center gap-3 font-mono text-xs">
          <div className="flex items-center gap-2">
            <span className="text-[#64748b]">Test Asset:</span>
            <select
              value={targetSymbol}
              onChange={(e) => setTargetSymbol(e.target.value)}
              className="bg-[#090d16] border border-[#1e293b] rounded px-3 py-1.5 text-white font-mono"
            >
              {["RELIANCE", "TCS", "HDFCBANK", "INFY", "TATAMOTORS", "NIFTY 50"].map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          <button
            onClick={handleRunBacktest}
            disabled={isBacktesting || !selectedStrategy}
            className="px-4 py-2 rounded bg-cyan-500 hover:bg-cyan-400 text-black font-bold flex items-center gap-2 transition disabled:opacity-50"
          >
            <Play className={`w-4 h-4 fill-current ${isBacktesting ? "animate-spin" : ""}`} />
            <span>{isBacktesting ? "Simulating Trades..." : "Run Backtest"}</span>
          </button>
        </div>
      </div>

      {/* Grid: Strategy Creator / Selector & Rule AST */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Templates & AI Prompt Generator */}
        <div className="space-y-4 font-mono text-xs">
          {/* Natural Language Prompt */}
          <div className="terminal-card p-4">
            <div className="flex items-center gap-2 text-white font-bold mb-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span>AI Strategy Creator (Natural Language)</span>
            </div>
            <textarea
              value={nlPrompt}
              onChange={(e) => setNlPrompt(e.target.value)}
              placeholder="e.g. Buy when 20-DMA volume surges above 1.5 z-score and RSI bounces off 40"
              className="w-full h-20 bg-[#090d16] border border-[#1e293b] rounded p-2.5 text-white placeholder-[#475569] text-xs focus:outline-none focus:border-cyan-500 font-mono resize-none"
            />
            <button
              onClick={handleGenerateNL}
              disabled={isGenerating || !nlPrompt.trim()}
              className="mt-2 w-full py-2 bg-[#151b2c] hover:bg-[#1e293b] border border-[#1e293b] text-cyan-400 font-bold rounded flex items-center justify-center gap-2 transition disabled:opacity-50"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{isGenerating ? "Synthesizing DSL..." : "Generate Strategy DSL"}</span>
            </button>
          </div>

          {/* Curated Templates */}
          <div className="terminal-card p-4">
            <div className="text-white font-bold mb-3">CURATED STRATEGY TEMPLATES</div>
            <div className="space-y-2">
              {templates.map((tpl) => {
                const isSelected = selectedStrategy?.strategy_id === tpl.strategy_id;
                return (
                  <div
                    key={tpl.strategy_id}
                    onClick={() => setSelectedStrategy(tpl)}
                    className={`p-3 rounded border cursor-pointer transition ${
                      isSelected
                        ? "bg-cyan-500/10 border-cyan-500/50 text-white"
                        : "bg-[#090d16] border-[#1e293b] text-[#94a3b8] hover:border-[#334155]"
                    }`}
                  >
                    <div className="font-bold flex items-center justify-between">
                      <span>{tpl.name}</span>
                      {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />}
                    </div>
                    <div className="text-[10px] text-[#64748b] mt-1 line-clamp-2">
                      {tpl.description}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right: Active DSL Rule Inspector */}
        <div className="lg:col-span-2 space-y-4">
          <div className="terminal-card p-5">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#1e293b]">
              <div>
                <h3 className="text-sm font-bold font-mono text-white">
                  {selectedStrategy?.name || "Select or Generate a Strategy"}
                </h3>
                <div className="text-xs text-[#64748b] font-mono mt-0.5">
                  DSL Strategy ID: <span className="text-cyan-400">{selectedStrategy?.strategy_id}</span>
                </div>
              </div>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#151b2c] text-emerald-400 border border-emerald-500/30">
                JSON-Schema Validated
              </span>
            </div>

            {/* Entry Rules DSL Card */}
            <div className="space-y-4 font-mono text-xs">
              <div className="bg-[#090d16] p-4 rounded-lg border border-[#1e293b]">
                <div className="text-[#64748b] text-[11px] uppercase font-bold mb-2">ENTRY CONDITIONS (DSL AST):</div>
                <div className="space-y-2">
                  {selectedStrategy?.entry_rules?.conditions?.map((cond: any, idx: number) => (
                    <div key={idx} className="flex items-center gap-2 p-2 bg-[#0d121f] rounded border border-[#1e293b]/70">
                      <span className="text-cyan-400 font-bold">{cond.feature}</span>
                      <span className="text-amber-400 font-bold">{cond.operator}</span>
                      <span className="text-white font-bold">{String(cond.threshold)}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Risk Management Specification */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                  <div className="text-[10px] text-[#64748b]">Stop Loss</div>
                  <div className="text-sm font-bold text-rose-400 mt-0.5">
                    {selectedStrategy?.risk_management?.stop_loss_pct ?? 2.5}%
                  </div>
                </div>
                <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                  <div className="text-[10px] text-[#64748b]">Take Profit</div>
                  <div className="text-sm font-bold text-emerald-400 mt-0.5">
                    {selectedStrategy?.risk_management?.take_profit_pct ?? 6.0}%
                  </div>
                </div>
                <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                  <div className="text-[10px] text-[#64748b]">Indian Broker & STT</div>
                  <div className="text-sm font-bold text-white mt-0.5">0.10% (Delivery)</div>
                </div>
              </div>
            </div>
          </div>

          {/* Backtest Results View */}
          {backtestResult && metrics && (
            <div className="terminal-card p-5 space-y-4 animate-in fade-in duration-300">
              <div className="flex items-center justify-between pb-3 border-b border-[#1e293b]">
                <div className="flex items-center gap-2">
                  <BarChart2 className="w-4 h-4 text-cyan-400" />
                  <span className="text-sm font-bold font-mono text-white">BACKTEST PERFORMANCE REPORT</span>
                </div>
                <span className="text-xs font-mono text-[#64748b]">
                  Run ID: {backtestResult.run_id}
                </span>
              </div>

              {/* KPI Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-center">
                <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                  <div className="text-[10px] text-[#64748b]">Total Return</div>
                  <div className={`text-base font-bold mt-1 ${metrics.total_return_pct >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                    {metrics.total_return_pct >= 0 ? `+${metrics.total_return_pct}%` : `${metrics.total_return_pct}%`}
                  </div>
                </div>
                <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                  <div className="text-[10px] text-[#64748b]">Sharpe Ratio</div>
                  <div className="text-base font-bold text-cyan-400 mt-1">
                    {metrics.sharpe_ratio}
                  </div>
                </div>
                <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                  <div className="text-[10px] text-[#64748b]">Max Drawdown</div>
                  <div className="text-base font-bold text-rose-400 mt-1">
                    -{metrics.max_drawdown_pct}%
                  </div>
                </div>
                <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                  <div className="text-[10px] text-[#64748b]">Win Rate</div>
                  <div className="text-base font-bold text-white mt-1">
                    {metrics.win_rate_pct}% ({metrics.winning_trades}/{metrics.total_trades})
                  </div>
                </div>
              </div>

              {/* Trade Log List */}
              <div className="space-y-2 font-mono text-xs">
                <div className="text-[#64748b] text-[11px] font-bold">EXECUTED TRADES LOG:</div>
                <div className="max-h-40 overflow-y-auto space-y-1.5">
                  {backtestResult.trades?.length === 0 ? (
                    <div className="text-[#64748b] text-center py-4">No trade triggers occurred in this historical window.</div>
                  ) : (
                    backtestResult.trades?.map((t: any, idx: number) => {
                      const isProfit = t.pnl_inr >= 0;
                      return (
                        <div key={idx} className="flex items-center justify-between p-2 bg-[#090d16] rounded border border-[#1e293b]/70 text-[11px]">
                          <div className="flex items-center gap-2">
                            <span className={isProfit ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                              {isProfit ? "+" : ""}{t.pnl_pct}%
                            </span>
                            <span className="text-[#94a3b8]">
                              {t.shares} shares @ ₹{t.entry_price} → ₹{t.exit_price}
                            </span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-[#64748b]">{t.exit_reason}</span>
                            <span className={isProfit ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
                              {isProfit ? "+" : ""}{formatINR(t.pnl_inr)}
                            </span>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
