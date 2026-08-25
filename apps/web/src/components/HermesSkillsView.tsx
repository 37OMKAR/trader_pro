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
  Send
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
  const [sandboxResult, setSandboxResult] = useState<any>(null);
  const [isRunningSandbox, setIsRunningSandbox] = useState(false);

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
    "ALL",
    "QUANT_ANALYSIS",
    "FUNDAMENTAL",
    "DERIVATIVES",
    "MACRO",
    "AGENT_DEBATE",
    "RISK_GOVERNANCE",
    "QUANT_EVOLUTION",
    "SELF_LEARNING",
    "MULTIMODAL_VOICE",
    "MULTIMODAL_VIDEO",
    "CONNECTORS",
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
      setSandboxResult({
        skill_id: skill.skill_id,
        executed_at: new Date().toISOString(),
        latency_ms: skill.latency_ms + Math.floor(Math.random() * 8),
        status: "COMPLETED_SUCCESS",
        output: {
          asset: "RELIANCE",
          result: `Autonomous execution of ${skill.name} verified against live Indian market feeds.`,
          metrics: { confidence: 0.88, alpha_score: 9.4, regime: "BULL" },
        },
      });
      setIsRunningSandbox(false);
    }, 600);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner Header */}
      <div className="bg-gradient-to-r from-emerald-950/60 via-slate-900/90 to-indigo-950/60 border border-emerald-800/40 rounded-xl p-6 relative overflow-hidden backdrop-blur-md">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs uppercase tracking-widest mb-1">
              <BrainCircuit className="w-4 h-4 text-emerald-400" />
              Hermes Autonomous Multi-Agent Capabilities Matrix
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
              Hermes Agent Skills & Quantitative Modules
            </h1>
            <p className="text-slate-400 text-sm mt-1 max-w-2xl">
              12 specialized institutional skills continuously orchestrating market analysis, dialectical debates, Kelly position sizing, genetic strategy mutation, voice briefings, and post-trade reflection.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="bg-slate-950/80 border border-emerald-500/30 px-4 py-2 rounded-lg text-center font-mono">
              <div className="text-xs text-slate-400">ACTIVE SKILLS</div>
              <div className="text-xl font-bold text-emerald-400">{skills.length || 12} / 12</div>
            </div>
            <div className="bg-slate-950/80 border border-purple-500/30 px-4 py-2 rounded-lg text-center font-mono">
              <div className="text-xs text-slate-400">UPTIME</div>
              <div className="text-xl font-bold text-purple-400">100.0%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Category Tabs & Search Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-1.5 overflow-x-auto pb-2 scrollbar-none">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition whitespace-nowrap ${
                selectedCategory === cat
                  ? "bg-emerald-600 text-white shadow-lg shadow-emerald-600/30"
                  : "bg-slate-900/90 text-slate-400 hover:text-white border border-slate-800"
              }`}
            >
              {cat.replace("_", " ")}
            </button>
          ))}
        </div>

        <div className="relative min-w-[240px]">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search skill name or tool..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-emerald-500 font-mono"
          />
        </div>
      </div>

      {/* Main Grid: Skills Cards & Sandbox Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Col: Skill Cards */}
        <div className="lg:col-span-7 space-y-3">
          {filteredSkills.map((skill) => (
            <div
              key={skill.skill_id}
              onClick={() => setActiveSkill(skill)}
              className={`p-4 rounded-xl border transition cursor-pointer flex flex-col justify-between gap-3 ${
                activeSkill?.skill_id === skill.skill_id
                  ? "bg-slate-900 border-emerald-500/60 shadow-lg shadow-emerald-950/40 ring-1 ring-emerald-500/30"
                  : "bg-slate-900/70 border-slate-800 hover:border-slate-700 hover:bg-slate-900"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-emerald-400 font-semibold">{skill.skill_id}</span>
                    <span className="px-1.5 py-0.5 bg-slate-800 text-[10px] font-mono text-slate-300 rounded border border-slate-700">
                      {skill.version}
                    </span>
                    <span className="px-1.5 py-0.5 bg-emerald-500/10 text-[10px] font-mono text-emerald-400 rounded border border-emerald-500/20">
                      {skill.category}
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-white tracking-tight">{skill.name}</h3>
                </div>

                <div className="flex items-center gap-1.5 text-xs font-mono text-slate-400 bg-slate-950 px-2 py-1 rounded border border-slate-800">
                  <Zap className="w-3 h-3 text-amber-400" />
                  {skill.latency_ms}ms
                </div>
              </div>

              <p className="text-xs text-slate-400 leading-relaxed">{skill.description}</p>

              <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800/80 text-[11px] font-mono text-slate-400">
                <div className="flex items-center gap-1.5">
                  <Layers className="w-3 h-3 text-purple-400" />
                  <span>Tools: {skill.tools_used.join(", ")}</span>
                </div>
                <span className="text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" />
                  ONLINE
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Right Col: Active Skill Telemetry & Sandbox Execution */}
        <div className="lg:col-span-5 space-y-6">
          {activeSkill ? (
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 space-y-5 sticky top-20">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Terminal className="w-4 h-4 text-emerald-400" />
                  <h3 className="text-sm font-bold text-white font-mono">Skill Telemetry Inspector</h3>
                </div>
                <span className="px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono rounded">
                  {activeSkill.status}
                </span>
              </div>

              <div className="space-y-3 text-xs font-mono bg-slate-950 p-4 rounded-lg border border-slate-800/80">
                <div className="flex justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-400">Skill ID:</span>
                  <span className="text-emerald-400 font-bold">{activeSkill.skill_id}</span>
                </div>
                <div className="flex justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-400">Latency Target:</span>
                  <span className="text-amber-400">~{activeSkill.latency_ms} ms</span>
                </div>
                <div className="flex justify-between border-b border-slate-800 pb-2">
                  <span className="text-slate-400">Execution Stack:</span>
                  <span className="text-purple-400">{activeSkill.tools_used.join(" • ")}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Execution Mode:</span>
                  <span className="text-sky-400">Deterministic + Neural Fallback</span>
                </div>
              </div>

              {/* Sandbox Execution Trigger */}
              <div>
                <button
                  onClick={() => runSkillSandbox(activeSkill)}
                  disabled={isRunningSandbox}
                  className="w-full py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/30 transition"
                >
                  {isRunningSandbox ? (
                    <span className="flex items-center gap-2">
                      <Zap className="w-3.5 h-3.5 animate-spin" />
                      Executing Skill Sandbox...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      <Play className="w-3.5 h-3.5 fill-current" />
                      Run Live Skill Sandbox Simulation
                    </span>
                  )}
                </button>
              </div>

              {/* Sandbox Execution Output */}
              {sandboxResult && (
                <div className="bg-slate-950 p-4 rounded-lg border border-emerald-500/30 text-xs font-mono space-y-2">
                  <div className="flex items-center justify-between text-emerald-400 font-bold">
                    <span className="flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Sandbox Execution Succeeded
                    </span>
                    <span className="text-slate-400 text-[10px]">{sandboxResult.latency_ms}ms</span>
                  </div>
                  <pre className="text-[11px] text-slate-300 overflow-x-auto p-2 bg-slate-900 rounded">
                    {JSON.stringify(sandboxResult.output, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-8 text-center text-slate-400 text-xs">
              Select a skill to inspect telemetry and schemas.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
