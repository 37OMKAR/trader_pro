"use client";

import React, { useState, useEffect } from "react";
import { 
  Globe, 
  Search, 
  RefreshCw, 
  ExternalLink, 
  ShieldAlert, 
  TrendingUp, 
  BrainCircuit, 
  FileText, 
  CheckCircle2, 
  Clock, 
  Building2, 
  Sparkles,
  Layers,
  ArrowUpRight,
  Database
} from "lucide-react";
import { MarketAPI } from "@/lib/api";
import { formatINR, formatPercent } from "@/lib/utils";

export function ResearchIntelligenceView() {
  const [symbol, setSymbol] = useState<string>("RELIANCE");
  const [researchData, setResearchData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchResearch = async (targetSymbol: string) => {
    setLoading(true);
    try {
      const data = await MarketAPI.getDeepResearch(targetSymbol);
      setResearchData(data);
    } catch (err) {
      console.error("Failed to load deep research:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResearch(symbol);
  }, [symbol]);

  const targetSymbols = [
    "RELIANCE",
    "TCS",
    "HDFCBANK",
    "INFY",
    "TATAMOTORS",
    "ICICIBANK",
    "SBIN",
    "BHARTIARTL",
    "ITC",
    "LT",
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner Header */}
      <div className="bg-gradient-to-r from-cyan-950/60 via-[#0a0f1d]/90 to-indigo-950/60 border border-cyan-500/30 rounded-2xl p-6 relative overflow-hidden backdrop-blur-xl shadow-2xl">
        <div className="absolute -right-10 -top-10 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-cyan-400 font-mono text-xs uppercase tracking-widest">
              <Globe className="w-4 h-4 text-cyan-400 animate-spin" style={{ animationDuration: "12s" }} />
              <span>TinyFish Real-Time Web Intelligence & Exchange Filings</span>
            </div>
            <h1 className="text-2xl lg:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
              <span>Corporate Research & Web Intelligence</span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 font-mono border border-cyan-500/40">
                LIVE TINYFISH
              </span>
            </h1>
            <p className="text-slate-300 text-sm max-w-3xl leading-relaxed">
              Automated corporate disclosures, management guidance, and earnings commentary scraped live via the official TinyFish Web Search API and synthesized by the Hermes-3 intelligence engine.
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <div className="bg-slate-950/80 border border-cyan-500/30 px-4 py-2.5 rounded-xl text-center font-mono">
              <div className="text-[10px] text-slate-400 uppercase">Search Engine</div>
              <div className="text-sm font-bold text-cyan-400">TinyFish Live</div>
            </div>
            <div className="bg-slate-950/80 border border-emerald-500/30 px-4 py-2.5 rounded-xl text-center font-mono">
              <div className="text-[10px] text-slate-400 uppercase">Synthesis Brain</div>
              <div className="text-sm font-bold text-emerald-400">Hermes-3 70B</div>
            </div>
          </div>
        </div>
      </div>

      {/* Target Asset Selector & Status */}
      <div className="terminal-card p-4 flex flex-wrap items-center justify-between gap-4 font-mono text-xs">
        <div className="flex items-center gap-3">
          <span className="text-slate-400 font-semibold flex items-center gap-1.5">
            <Building2 className="w-4 h-4 text-cyan-400" />
            TARGET EQUITIES:
          </span>
          <div className="flex flex-wrap items-center gap-1.5">
            {targetSymbols.map((sym) => (
              <button
                key={sym}
                onClick={() => setSymbol(sym)}
                className={`px-3 py-1 rounded-md transition font-mono ${
                  symbol === sym
                    ? "bg-cyan-600 text-white shadow-lg shadow-cyan-600/30 ring-1 ring-cyan-400 font-bold"
                    : "bg-slate-900 text-slate-400 hover:text-white border border-slate-800"
                }`}
              >
                {sym}
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={() => fetchResearch(symbol)}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#151b2c] hover:bg-[#1e293b] text-slate-300 hover:text-white border border-slate-800 transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-cyan-400" : ""}`} />
          <span>{loading ? "Scraping Web..." : "Refresh Intelligence"}</span>
        </button>
      </div>

      {/* Main Research Content */}
      {loading ? (
        <div className="terminal-card p-16 text-center space-y-3">
          <Globe className="w-8 h-8 text-cyan-400 animate-spin mx-auto" />
          <div className="text-cyan-400 font-mono text-sm font-semibold">
            Querying TinyFish Web Engine & Synthesizing Filings for {symbol}...
          </div>
          <div className="text-slate-500 font-mono text-xs">
            Fetching quarterly disclosures, capital expenditure guidance, and board resolutions.
          </div>
        </div>
      ) : researchData ? (
        <div className="space-y-6">
          {/* Quick Snapshot Card */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 font-mono">
            <div className="terminal-card p-4 space-y-1">
              <div className="text-slate-400 text-[10px]">COMPANY</div>
              <div className="text-base font-bold text-white truncate">{researchData.company_name}</div>
              <div className="text-xs text-cyan-400">{researchData.sector}</div>
            </div>

            <div className="terminal-card p-4 space-y-1">
              <div className="text-slate-400 text-[10px]">LIVE SPOT PRICE</div>
              <div className="text-lg font-bold text-white">₹{researchData.current_price?.toLocaleString("en-IN")}</div>
              <div className={`text-xs ${researchData.percent_change >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                {researchData.percent_change >= 0 ? "+" : ""}{researchData.percent_change}%
              </div>
            </div>

            <div className="terminal-card p-4 space-y-1">
              <div className="text-slate-400 text-[10px]">INSTITUTIONAL GRADE</div>
              <div className="text-base font-bold text-emerald-400">{researchData.research_grade}</div>
              <div className="text-xs text-slate-400">SEBI & Quantitative Rating</div>
            </div>

            <div className="terminal-card p-4 space-y-1">
              <div className="text-slate-400 text-[10px]">RESEARCH TIMESTAMP</div>
              <div className="text-xs font-bold text-purple-400 truncate">{researchData.timestamp}</div>
              <div className="text-[10px] text-slate-500">IST Market Session</div>
            </div>
          </div>

          {/* Synthesis Memo */}
          <div className="terminal-card p-6 space-y-4">
            <div className="flex items-center gap-2 text-white font-bold font-mono text-sm border-b border-slate-800 pb-3">
              <BrainCircuit className="w-5 h-5 text-emerald-400" />
              <span>HERMES INTELLIGENCE SYNTHESIS (TINYFISH GROUNDED)</span>
            </div>
            <div className="text-xs font-mono text-slate-300 leading-relaxed whitespace-pre-line bg-slate-950 p-4 rounded-xl border border-slate-800/80">
              {researchData.llm_synthesis}
            </div>
          </div>

          {/* Dual Columns: Findings & Risk Factors */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Executive Findings */}
            <div className="terminal-card p-5 space-y-4">
              <div className="flex items-center gap-2 text-white font-bold font-mono text-xs">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <span>EXECUTIVE CORPORATE FINDINGS</span>
              </div>
              <div className="space-y-2.5 font-mono text-xs">
                {researchData.executive_findings?.map((item: string, i: number) => (
                  <div key={i} className="flex items-start gap-2 text-slate-300 bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Identified Risk Factors */}
            <div className="terminal-card p-5 space-y-4">
              <div className="flex items-center gap-2 text-white font-bold font-mono text-xs">
                <ShieldAlert className="w-4 h-4 text-rose-400" />
                <span>IDENTIFIED RISK FACTORS & HEADWINDS</span>
              </div>
              <div className="space-y-2.5 font-mono text-xs">
                {researchData.identified_risk_factors?.map((risk: string, i: number) => (
                  <div key={i} className="flex items-start gap-2 text-slate-300 bg-slate-950/60 p-3 rounded-lg border border-slate-800">
                    <ShieldAlert className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                    <span>{risk}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Live Web Sources & Citations from TinyFish */}
          <div className="terminal-card p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2 text-white font-bold font-mono text-xs">
                <FileText className="w-4 h-4 text-purple-400" />
                <span>TINYFISH LIVE CITATIONS & WEB SOURCES ({researchData.research_sources?.length || 0})</span>
              </div>
              <span className="text-[10px] font-mono text-slate-400">Verified Web Index</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
              {researchData.research_sources?.map((src: any, idx: number) => (
                <a
                  key={idx}
                  href={src.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800 hover:border-cyan-500/50 hover:bg-slate-900 transition flex flex-col justify-between gap-2 group"
                >
                  <div className="space-y-1">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-cyan-400 font-bold truncate group-hover:text-cyan-300">
                        {src.title}
                      </span>
                      <ArrowUpRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-cyan-400 shrink-0 transition" />
                    </div>
                    <p className="text-slate-400 text-[11px] line-clamp-2 leading-relaxed">
                      {src.snippet}
                    </p>
                  </div>
                  <div className="text-[10px] text-slate-500 truncate pt-1 border-t border-slate-800/60">
                    Source: {src.source || src.url}
                  </div>
                </a>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
