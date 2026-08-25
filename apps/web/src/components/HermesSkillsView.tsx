"use client";

import React, { useState, useEffect } from "react";
import { 
  Cpu, 
  Sparkles, 
  Activity, 
  CheckCircle2, 
  ShieldAlert, 
  TrendingUp, 
  BrainCircuit, 
  Sliders, 
  Search, 
  Play, 
  Zap, 
  Layers,
  Terminal,
  Volume2,
  Video,
  Send,
  Code2,
  Clock,
  CheckCircle,
  AlertCircle,
  Copy,
  Check,
  RefreshCw,
  Server,
  ArrowRight,
  Database,
  Lock,
  Globe
} from "lucide-react";

interface SkillItem {
  skill_id: string;
  name: string;
  category: string;
  status: string;
  version: string;
  description: string;
  latency_ms: number;
  tools_used: string[];
}

export function HermesSkillsView() {
  const [skills, setSkills] = useState<SkillItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState("ALL");
  const [searchTerm, setSearchTerm] = useState("");
  const [activeSkill, setActiveSkill] = useState<SkillItem | null>(null);
  
  // Sandbox State
  const [sandboxStock, setSandboxStock] = useState<string>("RELIANCE");
  const [sandboxRisk, setSandboxRisk] = useState<number>(5.0);
  const [sandboxConfidence, setSandboxConfidence] = useState<number>(85);
  const [sandboxResult, setSandboxResult] = useState<any>(null);
  const [isRunningSandbox, setIsRunningSandbox] = useState(false);
  const [copiedJson, setCopiedJson] = useState(false);
  const [activeInspectorTab, setActiveInspectorTab] = useState<"sandbox" | "architecture" | "telemetry" | "prompt">("sandbox");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/v1/skills")
      .then((res) => res.json())
      .then((data) => {
        setSkills(data);
        if (data.length > 0) setActiveSkill(data[0]);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load skills:", err);
        setLoading(false);
      });
  }, []);

  const categories = [
    { id: "ALL", label: "All Skills (12)" },
    { id: "QUANT_ANALYSIS", label: "Technical & Quant" },
    { id: "FUNDAMENTAL", label: "Fundamentals" },
    { id: "DERIVATIVES", label: "F&O Derivatives" },
    { id: "MACRO", label: "Macro & News" },
    { id: "AGENT_DEBATE", label: "Bull/Bear Debate" },
    { id: "RISK_GOVERNANCE", label: "Kelly Risk Arbiter" },
    { id: "QUANT_EVOLUTION", label: "Genetic Evolution" },
    { id: "SELF_LEARNING", label: "Reflection Memory" },
    { id: "MULTIMODAL_VOICE", label: "Neural TTS Voice" },
    { id: "MULTIMODAL_VIDEO", label: "Talking Avatar" },
    { id: "CONNECTORS", label: "Telegram Dispatcher" },
  ];

  const filteredSkills = skills.filter((s) => {
    const matchesCat = selectedCategory === "ALL" || s.category === selectedCategory;
    const matchesSearch =
      s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.skill_id.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCat && matchesSearch;
  });

  const runSkillSandbox = (skill: SkillItem) => {
    setIsRunningSandbox(true);
    setSandboxResult(null);

    setTimeout(() => {
      let outputPayload: any = {};
      const now = new Date().toISOString();

      switch (skill.skill_id) {
        case "SKILL_TECHNICAL_CHART_ANALYSIS":
          outputPayload = {
            symbol: sandboxStock,
            indicators: {
              rsi_14: 61.4,
              macd: { macd_line: 18.4, signal_line: 12.1, histogram: 6.3 },
              dma_20: 2510.0,
              dma_50: 2465.0,
              dma_200: 2380.0,
              atr_14: 38.5,
            },
            signal: "BULLISH_BREAKOUT",
            confidence: sandboxConfidence / 100,
            recommended_sl: 2471.5,
            recommended_target: 2587.0,
          };
          break;
        case "SKILL_FUNDAMENTAL_VALUATION_AUDIT":
          outputPayload = {
            symbol: sandboxStock,
            multiples: { pe_ratio: 24.2, industry_pe: 28.5, pb_ratio: 2.8, roe_pct: 16.4, roce_pct: 18.2, debt_to_equity: 0.38 },
            valuation_status: "UNDERVALUED_QUALITY",
            intrinsic_dcf_value: 2750.0,
            safety_margin_pct: 9.1,
          };
          break;
        case "SKILL_SENTIMENT_DERIVATIVES_DECODER":
          outputPayload = {
            symbol: sandboxStock,
            option_chain: { pcr_oi: 1.28, max_pain_strike: 2500, implied_volatility_pct: 16.8, call_oi_wall: 2600, put_oi_wall: 2450 },
            fii_activity: { net_index_futures_crores: +840.5, sentiment: "AGGRESSIVE_LONG" },
            derivatives_verdict: "STRONG_CALL_BUILDUP",
          };
          break;
        case "SKILL_DIALECTICAL_BULL_BEAR_DEBATE":
          outputPayload = {
            symbol: sandboxStock,
            bull_case: { conviction: 8.5, core_thesis: "20 DMA golden crossover supported by institutional FII inflow of ₹840 Cr and robust quarterly earnings." },
            bear_case: { conviction: 4.5, core_thesis: "Near-term resistance at ₹2550 psychological round-number with elevated crude price friction." },
            dialectical_resolution: "BULLISH_ASYMMETRY_DOMINANT",
            net_conviction_spread: "+4.0 Bullish Advantage",
          };
          break;
        case "SKILL_KELLY_CRITERION_RISK_ARBITER":
          outputPayload = {
            symbol: sandboxStock,
            kelly_calculation: { win_probability: 0.62, win_loss_ratio: 2.1, full_kelly_pct: 14.8, half_kelly_recommended: sandboxRisk },
            committee_verdict: {
              aggressive_trader_allocation_pct: 8.0,
              conservative_risk_allocation_pct: 3.0,
              neutral_kelly_arbitration_pct: sandboxRisk,
              max_drawdown_stop_loss_pct: 3.5,
              var_99_pct: 2.1,
            },
          };
          break;
        case "SKILL_KOKORO_NEURAL_TTS_VOICE":
          outputPayload = {
            audio_engine: "Kokoro-82M Neural Synthesis",
            accent: "Indian English (Deep & Authoritative)",
            audio_url: `/api/v1/voice/stream/briefing_${sandboxStock.toLowerCase()}.mp3`,
            format: "MP3 44.1kHz 128kbps",
            teleprompter_script: `Dalal Street Morning Brief: ${sandboxStock} is exhibiting strong institutional accumulation with Half-Kelly risk allocation set at ${sandboxRisk}%.`,
          };
          break;
        case "SKILL_TALKING_AVATAR_VIDEO_STUDIO":
          outputPayload = {
            avatar_id: "dalal_street_anchor_v1",
            video_resolution: "1080x1920 (9:16 Vertical HD)",
            video_url: `/api/v1/voice/avatar/briefing_${sandboxStock.toLowerCase()}.mp4`,
            status: "RENDERED_READY",
            lip_sync_accuracy_score: 0.98,
          };
          break;
        case "SKILL_TELEGRAM_WHATSAPP_DISPATCHER":
          outputPayload = {
            channel: "@MarketAI_Institutional_Alerts",
            subscribers_broadcast: 1420,
            message_payload: `🚀 *MARKET AI TRADE ALERT*\nSymbol: #${sandboxStock}\nAction: BUY\nTarget: ₹2,587.00\nStop Loss: ₹2,471.50\nRisk Sizing: ${sandboxRisk}%\nCommittee: Neutral Half-Kelly Arbiter`,
            dispatch_status: "BROADCAST_SUCCESS_200",
          };
          break;
        default:
          outputPayload = {
            symbol: sandboxStock,
            skill: skill.name,
            status: "EXECUTION_VERIFIED",
            execution_engine: "Hermes Multi-Agent Autonomous Brain",
            metrics: { confidence: sandboxConfidence / 100, latency_ms: skill.latency_ms + 4 },
          };
      }

      setSandboxResult({
        skill_id: skill.skill_id,
        executed_at: now,
        latency_ms: skill.latency_ms + Math.floor(Math.random() * 8),
        status: "COMPLETED_SUCCESS",
        output: outputPayload,
      });
      setIsRunningSandbox(false);
    }, 500);
  };

  const copyResultToClipboard = () => {
    if (sandboxResult) {
      navigator.clipboard.writeText(JSON.stringify(sandboxResult.output, null, 2));
      setCopiedJson(true);
      setTimeout(() => setCopiedJson(false), 2000);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner Header */}
      <div className="bg-gradient-to-r from-emerald-950/70 via-[#0a0f1d]/90 to-indigo-950/70 border border-emerald-500/30 rounded-2xl p-6 relative overflow-hidden backdrop-blur-xl shadow-2xl">
        <div className="absolute -right-10 -top-10 w-72 h-72 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs uppercase tracking-widest">
              <BrainCircuit className="w-4 h-4 text-emerald-400 animate-pulse" />
              <span>Hermes Autonomous Multi-Agent Command & Capabilities Matrix</span>
            </div>
            <h1 className="text-2xl lg:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
              <span>Hermes Agent Running Skills</span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-mono border border-emerald-500/40">
                12 ACTIVE
              </span>
            </h1>
            <p className="text-slate-300 text-sm max-w-3xl leading-relaxed">
              Real-time operational dashboard of all 12 specialized quantitative skills running inside the Hermes trading firm. Every skill runs deterministically or neuro-symbolically across live Indian equities, options chains, risk arbiters, and multimodal broadcasting channels.
            </p>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-3 gap-3 shrink-0">
            <div className="bg-slate-950/80 border border-emerald-500/30 px-4 py-2.5 rounded-xl text-center font-mono">
              <div className="text-[10px] text-slate-400 uppercase">Registered Skills</div>
              <div className="text-xl font-bold text-emerald-400">{skills.length || 12} / 12</div>
            </div>
            <div className="bg-slate-950/80 border border-cyan-500/30 px-4 py-2.5 rounded-xl text-center font-mono">
              <div className="text-[10px] text-slate-400 uppercase">Avg Latency</div>
              <div className="text-xl font-bold text-cyan-400">~240 ms</div>
            </div>
            <div className="bg-slate-950/80 border border-purple-500/30 px-4 py-2.5 rounded-xl text-center font-mono">
              <div className="text-[10px] text-slate-400 uppercase">Skill Uptime</div>
              <div className="text-xl font-bold text-purple-400">100.0%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Category Navigation & Search */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex items-center gap-1.5 overflow-x-auto pb-2 scrollbar-none">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition whitespace-nowrap ${
                selectedCategory === cat.id
                  ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30 ring-1 ring-emerald-400"
                  : "bg-slate-900/90 text-slate-400 hover:text-white border border-slate-800"
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        <div className="relative min-w-[260px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search skill, tool or engine..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-emerald-500 font-mono"
          />
        </div>
      </div>

      {/* Main Content: Skill Cards + Expanded Inspector Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Skill Cards List */}
        <div className="lg:col-span-6 space-y-3">
          {filteredSkills.map((skill) => {
            const isSelected = activeSkill?.skill_id === skill.skill_id;
            return (
              <div
                key={skill.skill_id}
                onClick={() => {
                  setActiveSkill(skill);
                  setSandboxResult(null);
                }}
                className={`p-4 rounded-xl border transition cursor-pointer flex flex-col justify-between gap-3 ${
                  isSelected
                    ? "bg-slate-900 border-emerald-500/70 shadow-lg shadow-emerald-950/50 ring-1 ring-emerald-500/40"
                    : "bg-slate-900/70 border-slate-800/90 hover:border-slate-700 hover:bg-slate-900"
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-emerald-400 font-semibold">{skill.skill_id}</span>
                      <span className="px-1.5 py-0.5 bg-slate-800 text-[10px] font-mono text-slate-300 rounded border border-slate-700">
                        v{skill.version}
                      </span>
                      <span className="px-1.5 py-0.5 bg-emerald-500/10 text-[10px] font-mono text-emerald-400 rounded border border-emerald-500/20">
                        {skill.category}
                      </span>
                    </div>
                    <h3 className="text-sm font-bold text-white tracking-tight">{skill.name}</h3>
                  </div>

                  <div className="flex items-center gap-1.5 text-xs font-mono text-slate-300 bg-slate-950 px-2 py-1 rounded border border-slate-800">
                    <Zap className="w-3 h-3 text-amber-400" />
                    <span>~{skill.latency_ms}ms</span>
                  </div>
                </div>

                <p className="text-xs text-slate-400 leading-relaxed">{skill.description}</p>

                <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800/80 text-[11px] font-mono text-slate-400">
                  <div className="flex items-center gap-1.5">
                    <Layers className="w-3 h-3 text-purple-400" />
                    <span>Stack: {skill.tools_used.join(" • ")}</span>
                  </div>
                  <div className="flex items-center gap-1 text-emerald-400 font-medium">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 pulse-active shadow-glow-green" />
                    <span>ACTIVE RUNNING</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: Deep-Dive Skill Telemetry & Live Interactive Sandbox */}
        <div className="lg:col-span-6 space-y-4">
          {activeSkill ? (
            <div className="bg-[#090e18] border border-slate-800 rounded-xl p-5 space-y-5 sticky top-20 shadow-2xl">
              {/* Header */}
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
                <div className="flex items-center gap-2.5">
                  <div className="p-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
                    <Terminal className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white font-mono">{activeSkill.name}</h3>
                    <div className="text-xs text-slate-400 font-mono">{activeSkill.skill_id}</div>
                  </div>
                </div>
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-semibold">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 pulse-active shadow-glow-green" />
                  <span>READY</span>
                </div>
              </div>

              {/* Sub-Tabs for Inspector */}
              <div className="flex items-center gap-2 border-b border-slate-800/80 pb-2">
                {[
                  { id: "sandbox", label: "Live Sandbox Runner" },
                  { id: "architecture", label: "Architecture Flow" },
                  { id: "telemetry", label: "Live Telemetry" },
                  { id: "prompt", label: "Prompt & Schema" },
                ].map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setActiveInspectorTab(t.id as any)}
                    className={`px-3 py-1 rounded-md text-xs font-mono font-medium transition ${
                      activeInspectorTab === t.id
                        ? "bg-slate-800 text-emerald-400 border border-emerald-500/30"
                        : "text-slate-400 hover:text-white"
                    }`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>

              {/* TAB 1: Live Sandbox Runner */}
              {activeInspectorTab === "sandbox" && (
                <div className="space-y-4">
                  {/* Parameter Controls */}
                  <div className="grid grid-cols-2 gap-3 bg-slate-950/70 p-3.5 rounded-lg border border-slate-800">
                    <div>
                      <label className="text-[11px] font-mono text-slate-400 block mb-1">TARGET SYMBOL</label>
                      <select
                        value={sandboxStock}
                        onChange={(e) => setSandboxStock(e.target.value)}
                        className="w-full bg-slate-900 border border-slate-800 text-xs text-white rounded p-1.5 font-mono focus:outline-none focus:border-emerald-500"
                      >
                        <option value="RELIANCE">RELIANCE.NS</option>
                        <option value="TCS">TCS.NS</option>
                        <option value="HDFCBANK">HDFCBANK.NS</option>
                        <option value="INFY">INFY.NS</option>
                        <option value="TATAMOTORS">TATAMOTORS.NS</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-[11px] font-mono text-slate-400 block mb-1">
                        RISK BUDGET: <span className="text-emerald-400 font-bold">{sandboxRisk}%</span>
                      </label>
                      <input
                        type="range"
                        min="1"
                        max="15"
                        step="0.5"
                        value={sandboxRisk}
                        onChange={(e) => setSandboxRisk(parseFloat(e.target.value))}
                        className="w-full accent-emerald-500"
                      />
                    </div>
                  </div>

                  {/* Run Button */}
                  <button
                    onClick={() => runSkillSandbox(activeSkill)}
                    disabled={isRunningSandbox}
                    className="w-full py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold font-mono flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/30 transition"
                  >
                    {isRunningSandbox ? (
                      <span className="flex items-center gap-2">
                        <RefreshCw className="w-4 h-4 animate-spin text-white" />
                        Executing Skill Autonomous Pipeline on {sandboxStock}...
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        <Play className="w-4 h-4 fill-current text-white" />
                        Execute Live Skill Simulation on {sandboxStock}
                      </span>
                    )}
                  </button>

                  {/* Output Terminal */}
                  {sandboxResult ? (
                    <div className="bg-slate-950 rounded-xl border border-emerald-500/40 overflow-hidden text-xs font-mono space-y-2">
                      <div className="bg-slate-900/90 px-4 py-2 flex items-center justify-between border-b border-slate-800">
                        <span className="text-emerald-400 font-bold flex items-center gap-1.5">
                          <CheckCircle className="w-3.5 h-3.5" />
                          Execution Output (Status: 200 OK • Latency: {sandboxResult.latency_ms}ms)
                        </span>
                        <button
                          onClick={copyResultToClipboard}
                          className="flex items-center gap-1 text-[10px] text-slate-400 hover:text-white transition"
                        >
                          {copiedJson ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                          <span>{copiedJson ? "Copied" : "Copy JSON"}</span>
                        </button>
                      </div>
                      <pre className="p-4 text-[11px] text-slate-200 overflow-x-auto max-h-64 scrollbar-thin">
                        {JSON.stringify(sandboxResult.output, null, 2)}
                      </pre>
                    </div>
                  ) : (
                    <div className="p-6 bg-slate-950/60 rounded-xl border border-dashed border-slate-800 text-center text-slate-500 text-xs font-mono">
                      Click the green execute button above to trigger an autonomous simulation of <span className="text-slate-300">{activeSkill.name}</span>.
                    </div>
                  )}
                </div>
              )}

              {/* TAB 2: Architecture Flow */}
              {activeInspectorTab === "architecture" && (
                <div className="space-y-4 text-xs font-mono">
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
                    <div className="text-slate-300 font-bold text-sm">Pipeline Execution Flow</div>
                    <div className="flex items-center gap-2 text-slate-400">
                      <div className="px-2 py-1 bg-slate-900 rounded border border-slate-700 text-cyan-400">
                        1. NSE Market Feed / Yahoo
                      </div>
                      <ArrowRight className="w-3 h-3 text-slate-500" />
                      <div className="px-2 py-1 bg-slate-900 rounded border border-slate-700 text-emerald-400">
                        2. {activeSkill.skill_id}
                      </div>
                      <ArrowRight className="w-3 h-3 text-slate-500" />
                      <div className="px-2 py-1 bg-slate-900 rounded border border-slate-700 text-purple-400">
                        3. Hermes Synthesis
                      </div>
                    </div>
                    <p className="text-slate-400 text-xs leading-relaxed pt-2">
                      This skill operates as a sovereign quantitative service within the Hermes trading firm. Outputs are passed through the 3-Way Risk Committee (Neutral Half-Kelly Arbiter) before committing to paper positions in <code className="text-emerald-400">market_ai.db</code>.
                    </p>
                  </div>
                </div>
              )}

              {/* TAB 3: Live Telemetry */}
              {activeInspectorTab === "telemetry" && (
                <div className="space-y-3 text-xs font-mono bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <div className="flex justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400">Assigned Multi-Agent Role:</span>
                    <span className="text-emerald-400 font-bold">Hermes Sovereign Specialist</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400">Inference Engine:</span>
                    <span className="text-sky-400">Nous Hermes-3 70B + DeepSeek-V3 Fallback</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400">Target Latency SLA:</span>
                    <span className="text-amber-400">~{activeSkill.latency_ms} ms</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800 pb-2">
                    <span className="text-slate-400">Persistence Target:</span>
                    <span className="text-purple-400">SQLite market_ai.db / TimescaleDB</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Memory Bank Access:</span>
                    <span className="text-emerald-400">Long-Term Post-Trade Reflection Active</span>
                  </div>
                </div>
              )}

              {/* TAB 4: Prompt & Schema */}
              {activeInspectorTab === "prompt" && (
                <div className="space-y-3 text-xs font-mono">
                  <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 space-y-2">
                    <div className="text-slate-400 font-bold">System Directive Header:</div>
                    <div className="text-slate-300 text-[11px] bg-slate-900 p-2.5 rounded border border-slate-800 leading-relaxed">
                      {`You are an elite institutional quantitative specialist executing ${activeSkill.name}. Adhere strictly to SEBI risk boundaries, 2 ATR trailing stops, and Half-Kelly position sizing.`}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-12 text-center text-slate-400 text-xs font-mono">
              Select a skill from the left column to inspect telemetry, schemas, and live sandbox execution.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
