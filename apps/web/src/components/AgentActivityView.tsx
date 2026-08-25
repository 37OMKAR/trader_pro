"use client";

import React, { useState, useEffect } from "react";
import { Cpu, Users, MessageSquare, ShieldCheck, Play, Sparkles, RefreshCw, CheckCircle2, AlertTriangle, ArrowRight } from "lucide-react";
import { MarketAPI } from "@/lib/api";
import { formatINR, formatNumber, formatPercent } from "@/lib/utils";

export function AgentActivityView() {
  const [symbol, setSymbol] = useState<string>("RELIANCE");
  const [deliberation, setDeliberation] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const runSupervisoryWorkflow = async (targetSymbol: string) => {
    setLoading(true);
    try {
      const data = await MarketAPI.getAgentDeliberations(targetSymbol);
      setDeliberation(data);
    } catch (err) {
      console.error("Error running supervisory workflow:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runSupervisoryWorkflow(symbol);
  }, [symbol]);

  const quote = deliberation?.quote;
  const reports = deliberation?.analyst_reports;
  const debate = deliberation?.debate;
  const trade = deliberation?.trade_proposal;
  const risk = deliberation?.risk_evaluation;
  const pm = deliberation?.portfolio_decision;

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="terminal-card p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-cyan-400" />
            <h2 className="text-base font-bold font-mono text-white">
              HERMES SUPERVISOR HUB & AGENT ACTIVITY CENTER
            </h2>
          </div>
          <div className="text-xs text-[#64748b] font-mono mt-0.5">
            Live Deliberations from Fundamentals, Technicals, Sentiment, Debate Team & Risk Committee
          </div>
        </div>

        <div className="flex items-center gap-3 font-mono text-xs">
          <div className="flex items-center gap-2">
            <span className="text-[#64748b]">Asset Under Review:</span>
            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="bg-[#090d16] border border-[#1e293b] rounded px-3 py-1.5 text-white font-mono"
            >
              {["RELIANCE", "TCS", "HDFCBANK", "INFY", "TATAMOTORS", "SBIN"].map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          <button
            onClick={() => runSupervisoryWorkflow(symbol)}
            disabled={loading}
            className="p-2 rounded bg-[#151b2c] hover:bg-[#1e293b] text-[#94a3b8] hover:text-white border border-[#1e293b] transition"
            title="Re-run Deliberations"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-cyan-400" : ""}`} />
          </button>
        </div>
      </div>

      {loading ? (
        <div className="terminal-card p-16 text-center text-xs font-mono text-cyan-400 animate-pulse space-y-3">
          <div className="text-base font-bold">Orchestrating Autonomous Trading Committee for {symbol}...</div>
          <div className="text-[#64748b]">
            [1/4] Running Specialized Analysts → [2/4] TinyFish Web Intelligence → [3/4] Bull vs Bear Debate → [4/4] Risk Clearance
          </div>
        </div>
      ) : (
        <div className="space-y-6 font-mono text-xs">
          {/* Section 1: Executive Briefing Banner */}
          {deliberation?.hermes_executive_briefing && (
            <div className="terminal-card p-5 bg-gradient-to-r from-[#0c1220] via-[#10172c] to-[#151924] border-cyan-500/40">
              <div className="flex items-center justify-between pb-3 border-b border-[#1e293b] mb-3">
                <div className="flex items-center gap-2 text-white font-bold">
                  <Sparkles className="w-4 h-4 text-cyan-400" />
                  <span>HERMES CHIEF SUPERVISOR SYNTHESIS MEMO</span>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400">
                  {deliberation.supervisor}
                </span>
              </div>
              <div className="text-[#cbd5e1] leading-relaxed whitespace-pre-line text-[11px]">
                {deliberation.hermes_executive_briefing}
              </div>
            </div>
          )}

          {/* Section 2: Four Specialized Analyst Cards */}
          <div>
            <div className="text-white font-bold mb-3 uppercase tracking-wider text-[11px]">
              PHASE 1: SPECIALIZED ANALYST REPORTS
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Fundamentals */}
              <div className="terminal-card p-4 space-y-2">
                <div className="flex items-center justify-between text-cyan-400 font-bold">
                  <span>FUNDAMENTALS ANALYST</span>
                  <span className="text-[10px] text-[#64748b]">P/E & Balance Sheet</span>
                </div>
                <p className="text-[#94a3b8] text-[11px] leading-relaxed">
                  {reports?.fundamentals?.report || "Robust balance sheet metrics."}
                </p>
              </div>

              {/* Technicals */}
              <div className="terminal-card p-4 space-y-2">
                <div className="flex items-center justify-between text-emerald-400 font-bold">
                  <span>TECHNICAL PATTERN ANALYST</span>
                  <span className="text-[10px] text-[#64748b]">20/50/200 DMA & RSI</span>
                </div>
                <p className="text-[#94a3b8] text-[11px] leading-relaxed">
                  {reports?.technicals?.report || "Bullish moving average alignment."}
                </p>
              </div>

              {/* Sentiment */}
              <div className="terminal-card p-4 space-y-2">
                <div className="flex items-center justify-between text-purple-400 font-bold">
                  <span>SENTIMENT & DERIVATIVES ANALYST</span>
                  <span className="text-[10px] text-[#64748b]">PCR & Institutional Flows</span>
                </div>
                <p className="text-[#94a3b8] text-[11px] leading-relaxed">
                  {reports?.sentiment?.report || "Institutional base building."}
                </p>
              </div>

              {/* Macro & News */}
              <div className="terminal-card p-4 space-y-2">
                <div className="flex items-center justify-between text-amber-400 font-bold">
                  <span>MACROECONOMIC & POLICY ANALYST</span>
                  <span className="text-[10px] text-[#64748b]">RBI Stance & Global Yields</span>
                </div>
                <p className="text-[#94a3b8] text-[11px] leading-relaxed">
                  {reports?.macro?.report || "Steady GDP expansion."}
                </p>
              </div>
            </div>
          </div>

          {/* Section 3: Bull vs Bear Debate Arena */}
          {debate && (
            <div>
              <div className="text-white font-bold mb-3 uppercase tracking-wider text-[11px]">
                PHASE 2: RESEARCH TEAM DEBATE ARENA
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Bull Case */}
                <div className="terminal-card p-4 border-emerald-500/30 bg-emerald-950/10 space-y-2">
                  <div className="flex items-center gap-2 text-emerald-400 font-bold">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>BULLISH RESEARCHER THESIS</span>
                  </div>
                  <p className="text-[#cbd5e1] text-[11px] font-semibold">{debate.bull_case.thesis}</p>
                  <ul className="space-y-1 text-[#94a3b8] text-[10px]">
                    {debate.bull_case.catalysts?.map((c: string, i: number) => (
                      <li key={i}>+ {c}</li>
                    ))}
                  </ul>
                </div>

                {/* Bear Case */}
                <div className="terminal-card p-4 border-rose-500/30 bg-rose-950/10 space-y-2">
                  <div className="flex items-center gap-2 text-rose-400 font-bold">
                    <AlertTriangle className="w-4 h-4" />
                    <span>BEARISH RESEARCHER THESIS</span>
                  </div>
                  <p className="text-[#cbd5e1] text-[11px] font-semibold">{debate.bear_case.thesis}</p>
                  <ul className="space-y-1 text-[#94a3b8] text-[10px]">
                    {debate.bear_case.risks?.map((r: string, i: number) => (
                      <li key={i}>- {r}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Section 4: Lead Trader Proposal & Risk Clearance */}
          {trade && risk && pm && (
            <div>
              <div className="text-white font-bold mb-3 uppercase tracking-wider text-[11px]">
                PHASE 3 & 4: EXECUTION FORMULATION & RISK CLEARANCE
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-[#090d16] p-4 rounded-lg border border-[#1e293b]">
                  <div className="text-[#64748b] text-[10px]">PROPOSED ACTION</div>
                  <div className="text-lg font-bold text-emerald-400 mt-1">
                    {trade.action} @ ₹{trade.entry_price}
                  </div>
                  <div className="text-[10px] text-[#64748b] mt-1">
                    Target 1: ₹{trade.target_1} | Stop: ₹{trade.stop_loss}
                  </div>
                </div>

                <div className="bg-[#090d16] p-4 rounded-lg border border-[#1e293b]">
                  <div className="text-[#64748b] text-[10px]">RISK CLEARANCE</div>
                  <div className="text-lg font-bold text-cyan-400 mt-1">
                    {risk.verdict} ({risk.max_approved_shares} shares)
                  </div>
                  <div className="text-[10px] text-[#64748b] mt-1">
                    Max Capital: ₹{risk.capital_allocated_inr} | Risk/Reward: {trade.risk_reward_ratio}
                  </div>
                </div>

                <div className="bg-[#090d16] p-4 rounded-lg border border-[#1e293b]">
                  <div className="text-[#64748b] text-[10px]">PORTFOLIO AUTHORIZATION</div>
                  <div className="text-lg font-bold text-white mt-1">
                    {pm.status}
                  </div>
                  <div className="text-[10px] text-emerald-400 mt-1">
                    Executed in Virtual Portfolio
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
