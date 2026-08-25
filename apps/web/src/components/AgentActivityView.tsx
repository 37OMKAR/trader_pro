"use client";

import React, { useState, useEffect } from "react";
import {
  Users,
  Sparkles,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
  Flame,
  Scale,
  BrainCircuit,
  Download,
  BookOpen,
} from "lucide-react";
import { MarketAPI } from "@/lib/api";
import { formatINR, formatNumber, formatPercent } from "@/lib/utils";

export function AgentActivityView() {
  const [symbol, setSymbol] = useState<string>("RELIANCE");
  const [deliberation, setDeliberation] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeStage, setActiveStage] = useState<number>(0);

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
  const riskCommittee = deliberation?.risk_committee;
  const pastReflections = deliberation?.past_reflections;

  const downloadDossier = () => {
    if (!deliberation) return;
    const memo = deliberation.hermes_executive_briefing || "Institutional Analysis";
    const blob = new Blob([memo], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${symbol}_Institutional_Research_Dossier.md`;
    a.click();
  };

  const stages = [
    { id: 0, title: "1. Specialist Analysts", desc: "4 Parallel Streams" },
    { id: 1, title: "2. Dialectical Debate", desc: "Bull vs Bear Case" },
    { id: 2, title: "3. Trade Formulation", desc: "Order & R:R Targets" },
    { id: 3, title: "4. 3-Way Risk Committee", desc: "Aggressive / Conservative / Kelly" },
    { id: 4, title: "5. Synthesis & Memory", desc: "Executive Memo & Reflector" },
  ];

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
            5-Stage Trading Firm Architecture • Dialectical Debates • 3-Way Risk Committee • Reflection Memory
          </div>
        </div>

        <div className="flex items-center gap-3 font-mono text-xs">
          <div className="flex items-center gap-2">
            <span className="text-[#64748b]">Asset:</span>
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
            onClick={downloadDossier}
            disabled={!deliberation}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#151b2c] hover:bg-[#1e293b] text-cyan-400 border border-cyan-500/30 transition text-xs font-mono"
            title="Download Institutional Dossier"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Dossier (.md)</span>
          </button>

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

      {/* 5-Stage Interactive Pipeline Stepper */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-2 font-mono text-xs">
        {stages.map((st) => (
          <button
            key={st.id}
            onClick={() => setActiveStage(st.id)}
            className={`p-3 rounded-lg border text-left transition ${
              activeStage === st.id
                ? "bg-[#151d30] border-cyan-500/60 text-white shadow-lg shadow-cyan-950/30"
                : "bg-[#0c1220] border-[#1e293b] text-[#64748b] hover:text-[#94a3b8]"
            }`}
          >
            <div className="font-bold text-[11px] text-cyan-400">{st.title}</div>
            <div className="text-[10px] text-[#64748b] mt-0.5">{st.desc}</div>
          </button>
        ))}
      </div>

      {loading ? (
        <div className="terminal-card p-16 text-center text-xs font-mono text-cyan-400 animate-pulse space-y-3">
          <div className="text-base font-bold">Orchestrating 5-Stage Trading Firm Deliberations for {symbol}...</div>
          <div className="text-[#64748b]">
            [1/5] 4 Concurrent Analysts → [2/5] Dialectical Debate → [3/5] Lead Trader → [4/5] 3-Way Risk Committee → [5/5] Hermes Synthesis & Memory
          </div>
        </div>
      ) : (
        <div className="space-y-6 font-mono text-xs">
          {/* STAGE 0: SPECIALIZED ANALYSTS */}
          {(activeStage === 0 || activeStage === -1) && (
            <div className="space-y-3">
              <div className="text-white font-bold uppercase tracking-wider text-[11px] flex items-center gap-2">
                <span>STAGE 1: SPECIALIZED ANALYST REPORTS</span>
                <span className="text-[#64748b] text-[10px]">(Concurrent Market, Fundamental, Sentiment & Macro Feeds)</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Fundamentals */}
                <div className="terminal-card p-4 space-y-2">
                  <div className="flex items-center justify-between text-cyan-400 font-bold">
                    <span>FUNDAMENTALS ANALYST</span>
                    <span className="text-[10px] text-[#64748b]">P/E, ROE & Balance Sheet</span>
                  </div>
                  <p className="text-[#94a3b8] text-[11px] leading-relaxed">
                    {reports?.fundamentals?.summary || "Robust balance sheet metrics."}
                  </p>
                </div>

                {/* Technicals */}
                <div className="terminal-card p-4 space-y-2">
                  <div className="flex items-center justify-between text-emerald-400 font-bold">
                    <span>TECHNICAL PATTERN ANALYST</span>
                    <span className="text-[10px] text-[#64748b]">20/50/200 DMA & RSI</span>
                  </div>
                  <p className="text-[#94a3b8] text-[11px] leading-relaxed">
                    {reports?.technicals?.summary || "Bullish moving average alignment."}
                  </p>
                </div>

                {/* Sentiment */}
                <div className="terminal-card p-4 space-y-2">
                  <div className="flex items-center justify-between text-purple-400 font-bold">
                    <span>SENTIMENT & DERIVATIVES ANALYST</span>
                    <span className="text-[10px] text-[#64748b]">PCR & Institutional Inflows</span>
                  </div>
                  <p className="text-[#94a3b8] text-[11px] leading-relaxed">
                    {reports?.sentiment?.summary || "Institutional base building."}
                  </p>
                </div>

                {/* Macro & News */}
                <div className="terminal-card p-4 space-y-2">
                  <div className="flex items-center justify-between text-amber-400 font-bold">
                    <span>MACROECONOMIC & POLICY ANALYST</span>
                    <span className="text-[10px] text-[#64748b]">RBI Stance & Yields</span>
                  </div>
                  <p className="text-[#94a3b8] text-[11px] leading-relaxed">
                    {reports?.macro?.summary || "Steady GDP expansion."}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* STAGE 1: DIALECTICAL DEBATE */}
          {(activeStage === 1 || activeStage === -1) && debate && (
            <div className="space-y-3">
              <div className="text-white font-bold uppercase tracking-wider text-[11px] flex items-center gap-2">
                <span>STAGE 2: RESEARCH TEAM DIALECTICAL DEBATE</span>
                <span className="text-[#64748b] text-[10px]">(Bullish Growth Opportunities vs Bearish Downside Traps)</span>
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
                    {debate.bear_case.risk_triggers?.map((r: string, i: number) => (
                      <li key={i}>- {r}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* STAGE 2: LEAD TRADER PLAN */}
          {(activeStage === 2 || activeStage === -1) && trade && (
            <div className="space-y-3">
              <div className="text-white font-bold uppercase tracking-wider text-[11px]">
                STAGE 3: LEAD TRADER ORDER FORMULATION
              </div>
              <div className="terminal-card p-4 space-y-3 bg-[#0c1220]">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                    <div className="text-[#64748b] text-[10px]">TRANSACTION ACTION</div>
                    <div className="text-lg font-bold text-emerald-400 mt-1">{trade.action}</div>
                  </div>
                  <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                    <div className="text-[#64748b] text-[10px]">ENTRY PRICE</div>
                    <div className="text-lg font-bold text-white mt-1">₹{trade.entry_price}</div>
                  </div>
                  <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                    <div className="text-[#64748b] text-[10px]">TARGET 1 / STOP LOSS</div>
                    <div className="text-sm font-bold text-cyan-400 mt-1">₹{trade.target_1} / ₹{trade.stop_loss}</div>
                  </div>
                  <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                    <div className="text-[#64748b] text-[10px]">RISK / REWARD RATIO</div>
                    <div className="text-lg font-bold text-amber-400 mt-1">{trade.risk_reward_ratio}</div>
                  </div>
                </div>
                <div className="text-[#94a3b8] text-[11px] leading-relaxed border-t border-[#1e293b] pt-2">
                  <span className="text-white font-semibold">Trader Rationale: </span>
                  {trade.rationale}
                </div>
              </div>
            </div>
          )}

          {/* STAGE 3: 3-WAY RISK COMMITTEE ARENA */}
          {(activeStage === 3 || activeStage === -1) && riskCommittee && (
            <div className="space-y-3">
              <div className="text-white font-bold uppercase tracking-wider text-[11px] flex items-center gap-2">
                <span>STAGE 4: 3-WAY RISK COMMITTEE ARENA</span>
                <span className="text-[#64748b] text-[10px]">(Aggressive Growth vs Conservative Defense vs Kelly Arbiter)</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Aggressive */}
                <div className="terminal-card p-4 border-amber-500/30 bg-amber-950/10 space-y-2">
                  <div className="flex items-center gap-2 text-amber-400 font-bold">
                    <Flame className="w-4 h-4" />
                    <span>AGGRESSIVE DEBATOR</span>
                  </div>
                  <div className="text-[10px] text-amber-300 font-mono">
                    Rec. Allocation: {riskCommittee.aggressive.recommended_allocation_pct}%
                  </div>
                  <p className="text-[#cbd5e1] text-[10px] leading-relaxed">
                    {riskCommittee.aggressive.argument}
                  </p>
                </div>

                {/* Conservative */}
                <div className="terminal-card p-4 border-blue-500/30 bg-blue-950/10 space-y-2">
                  <div className="flex items-center gap-2 text-blue-400 font-bold">
                    <ShieldCheck className="w-4 h-4" />
                    <span>CONSERVATIVE GUARDIAN</span>
                  </div>
                  <div className="text-[10px] text-blue-300 font-mono">
                    Rec. Allocation: {riskCommittee.conservative.recommended_allocation_pct}%
                  </div>
                  <p className="text-[#cbd5e1] text-[10px] leading-relaxed">
                    {riskCommittee.conservative.argument}
                  </p>
                </div>

                {/* Neutral Kelly Arbiter */}
                <div className="terminal-card p-4 border-cyan-500/40 bg-cyan-950/20 space-y-2">
                  <div className="flex items-center gap-2 text-cyan-400 font-bold">
                    <Scale className="w-4 h-4" />
                    <span>KELLY QUANT ARBITER</span>
                  </div>
                  <div className="text-[10px] text-cyan-300 font-mono font-bold">
                    Approved: {riskCommittee.neutral_arbitration.approved_allocation_pct}% Capital
                  </div>
                  <p className="text-[#cbd5e1] text-[10px] leading-relaxed">
                    {riskCommittee.neutral_arbitration.consensus_summary}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* STAGE 4: SYNTHESIS & REFLECTION MEMORY */}
          {(activeStage === 4 || activeStage === -1) && (
            <div className="space-y-4">
              {/* Executive Briefing Banner */}
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

              {/* Reflection & Memory Bank */}
              {pastReflections && pastReflections.length > 0 && (
                <div className="terminal-card p-4 space-y-2 bg-[#090d16]">
                  <div className="flex items-center gap-2 text-cyan-400 font-bold text-[11px]">
                    <BookOpen className="w-4 h-4" />
                    <span>AGENT REFLECTION & DECISION MEMORY BANK</span>
                  </div>
                  <div className="space-y-2">
                    {pastReflections.map((ref: any, idx: number) => (
                      <div key={idx} className="p-2.5 rounded bg-[#0c1220] border border-[#1e293b] text-[10px] text-[#94a3b8]">
                        <div className="flex items-center justify-between text-[#64748b] mb-1">
                          <span className="text-white font-bold">{ref.symbol} • {ref.trade_action}</span>
                          <span className={ref.alpha_vs_nifty_pct >= 0 ? "text-emerald-400" : "text-rose-400"}>
                            Alpha vs NIFTY: {ref.alpha_vs_nifty_pct > 0 ? `+${ref.alpha_vs_nifty_pct}` : ref.alpha_vs_nifty_pct}%
                          </span>
                        </div>
                        <div>{ref.lesson}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
