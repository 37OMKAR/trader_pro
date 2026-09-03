"use client";

import React from "react";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

type Item = { id: string; label: string; hint?: string };

const TIERS: { key: string; roman: string; title: string; promise: string; items: Item[] }[] = [
  {
    key: "watch",
    roman: "I",
    title: "Watch",
    promise: "What the firm is doing right now, and the market it's doing it in.",
    items: [
      { id: "suite",       label: "The Suite · live floor",  hint: "all agents · live" },
      { id: "overview",    label: "The Firm · front page",   hint: "today's lead + ledger" },
      { id: "indices",     label: "Indices",                 hint: "NIFTY · SENSEX · BANK" },
      { id: "stocks",      label: "Equities",                hint: "large-cap universe" },
      { id: "sectors",     label: "Sectors & heatmap" },
      { id: "derivatives", label: "F&O derivatives" },
    ],
  },
  {
    key: "learn",
    roman: "II",
    title: "Learn",
    promise: "Understand every decision. Read the debates and the reasoning.",
    items: [
      { id: "agentactivity", label: "Agent conversations",   hint: "5-stage transcripts" },
      { id: "predictions",   label: "AI predictions" },
      { id: "research",      label: "Web research",          hint: "TinyFish" },
      { id: "skills",        label: "Hermes skills matrix" },
      { id: "tutor",         label: "Market tutor" },
      { id: "avatar",        label: "Talking avatar",        hint: "spoken briefing" },
    ],
  },
  {
    key: "trade",
    roman: "III",
    title: "Trade",
    promise: "The paper fund the firm is trading. Your intervention lives here.",
    items: [
      { id: "paper",       label: "Paper portfolio" },
      { id: "risk",        label: "Portfolio risk" },
      { id: "strategies",  label: "Strategy lab" },
      { id: "tournaments", label: "Strategy tournaments" },
      { id: "alerts",      label: "Alerts" },
      { id: "telegram",    label: "Telegram" },
    ],
  },
];

export function Sidebar({ activeTab, setActiveTab }: SidebarProps) {
  return (
    <aside
      className="h-screen sticky top-0 overflow-y-auto"
      style={{
        width: 300,
        background: "var(--paper)",
        borderRight: "1px solid var(--rule-strong)",
        padding: "28px 24px",
        boxSizing: "border-box",
      }}
    >
      {/* Masthead */}
      <div style={{ borderBottom: "3px double var(--rule-strong)", paddingBottom: 16 }}>
        <div className="eyebrow">Vol. III · Session live</div>
        <div className="serif" style={{ fontSize: 44, lineHeight: 0.95, marginTop: 4 }}>The Firm</div>
        <div className="serif" style={{ fontSize: 14, fontStyle: "italic", color: "var(--ink-subtle)", marginTop: 2 }}>
          a daily register of what the machines decided
        </div>
      </div>

      {/* Tiers */}
      {TIERS.map((tier) => (
        <div key={tier.key} style={{ marginTop: 24 }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
            <span className="serif" style={{ fontSize: 22, color: "var(--accent)", lineHeight: 1 }}>{tier.roman}.</span>
            <span className="serif" style={{ fontSize: 22, lineHeight: 1 }}>{tier.title}</span>
          </div>
          <div style={{ fontSize: 11, color: "var(--ink-subtle)", marginTop: 4, lineHeight: 1.4 }}>
            {tier.promise}
          </div>

          <ul style={{ margin: "10px 0 0 0", padding: 0, listStyle: "none" }}>
            {tier.items.map((item) => {
              const active = activeTab === item.id;
              return (
                <li key={item.id}>
                  <button
                    onClick={() => setActiveTab(item.id)}
                    className="w-full text-left"
                    style={{
                      padding: "8px 10px",
                      margin: "1px 0",
                      background: active ? "var(--ink)" : "transparent",
                      color: active ? "var(--paper)" : "var(--ink)",
                      border: "none",
                      cursor: "pointer",
                      fontFamily: "inherit",
                      fontSize: 13,
                      display: "flex",
                      alignItems: "baseline",
                      justifyContent: "space-between",
                      gap: 8,
                    }}
                  >
                    <span style={{ fontWeight: active ? 600 : 500 }}>{item.label}</span>
                    {item.hint && (
                      <span
                        className="mono"
                        style={{
                          fontSize: 9,
                          color: active ? "rgba(244,239,228,0.65)" : "var(--ink-subtle)",
                          textTransform: "uppercase",
                          letterSpacing: "0.08em",
                        }}
                      >
                        {item.hint}
                      </span>
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      ))}

      {/* Footer */}
      <div style={{ marginTop: 32, paddingTop: 16, borderTop: "1px solid var(--rule-strong)" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span
              className="pulse-active"
              style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--accent)", display: "inline-block" }}
            />
            <span style={{ fontSize: 12 }}>Hermes core</span>
          </div>
          <span className="mono" style={{ fontSize: 10, color: "var(--accent)", fontWeight: 700, letterSpacing: "0.14em" }}>
            LIVE
          </span>
        </div>
        <div style={{ fontSize: 10, color: "var(--ink-subtle)", marginTop: 6, lineHeight: 1.4 }}>
          Autonomous daemon cycling the large-cap universe · one deliberation every ~2 min.
        </div>
      </div>
    </aside>
  );
}
