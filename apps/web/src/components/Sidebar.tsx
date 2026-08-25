"use client";

import React from "react";
import {
  TrendingUp,
  LayoutDashboard,
  Layers,
  Zap,
  Cpu,
  FlaskConical,
  Briefcase,
  ShieldAlert,
  GraduationCap,
  Settings,
  Flame,
  PieChart,
} from "lucide-react";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export function Sidebar({ activeTab, setActiveTab }: SidebarProps) {
  const navSections = [
    {
      title: "MARKET",
      items: [
        { id: "overview", label: "Overview", icon: LayoutDashboard },
        { id: "indices", label: "Indices", icon: TrendingUp },
        { id: "stocks", label: "Equities", icon: Layers },
        { id: "derivatives", label: "F&O Derivatives", icon: Flame },
        { id: "sectors", label: "Sectors & Heatmap", icon: PieChart },
      ],
    },
    {
      title: "AI & QUANT",
      items: [
        { id: "predictions", label: "AI Predictions", icon: Cpu },
        { id: "signals", label: "Quant Signals", icon: Zap },
        { id: "strategylab", label: "Strategy Lab", icon: FlaskConical },
      ],
    },
    {
      title: "PORTFOLIO & RISK",
      items: [
        { id: "paper", label: "Paper Trading", icon: Briefcase },
        { id: "risk", label: "Risk Engine", icon: ShieldAlert },
      ],
    },
    {
      title: "SYSTEM",
      items: [
        { id: "tutor", label: "AI Market Tutor", icon: GraduationCap },
        { id: "settings", label: "Settings & APIs", icon: Settings },
      ],
    },
  ];

  return (
    <aside className="w-64 bg-[#090d16] border-r border-[#1e293b] flex flex-col h-screen shrink-0 select-none">
      {/* Brand Header */}
      <div className="h-16 px-5 border-b border-[#1e293b] flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-emerald-400 flex items-center justify-center font-bold text-black text-sm shadow-glow-cyan">
          AI
        </div>
        <div>
          <div className="font-bold tracking-wider text-sm text-white flex items-center gap-1.5">
            MARKET AI <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-mono">INDIA</span>
          </div>
          <div className="text-[11px] text-[#64748b] font-mono">INSTITUTIONAL v1.0</div>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {navSections.map((sec) => (
          <div key={sec.title}>
            <div className="px-3 text-[11px] font-semibold text-[#475569] tracking-wider uppercase mb-1.5">
              {sec.title}
            </div>
            <div className="space-y-0.5">
              {sec.items.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-all ${
                      isActive
                        ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm"
                        : "text-[#94a3b8] hover:text-white hover:bg-[#151b2c]"
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? "text-cyan-400" : "text-[#64748b]"}`} />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Bottom User / Engine Status */}
      <div className="p-3 border-t border-[#1e293b] bg-[#070a10]">
        <div className="p-2.5 rounded-lg bg-[#0e131f] border border-[#1e293b]/70 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-400 pulse-active shadow-glow-green" />
            <span className="text-[11px] text-[#94a3b8] font-mono">HERMES CORE</span>
          </div>
          <span className="text-[10px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded font-mono font-medium">READY</span>
        </div>
      </div>
    </aside>
  );
}
