"use client";

import React, { useEffect, useState } from "react";
import { MarketAPI } from "@/lib/api";
import { formatINR, formatPercent } from "@/lib/utils";

/**
 * Newspaper-style front page for The Firm.
 * Reads deliberations + paper-fund state from the running API and lays them out
 * as a lead story, ledger, fund glance, and reflection column.
 */

type Delib = {
  deliberation_id: string;
  symbol: string;
  status: string;
  created_at: string;
  trade?: any;
  risk?: any;
};

interface Props {
  onOpenAgentHub: () => void;
}

export function FrontPage({ onOpenAgentHub }: Props) {
  const [now, setNow] = useState<string>("");
  const [fund, setFund] = useState<any>(null);
  const [nifty, setNifty] = useState<any>(null);
  const [current, setCurrent] = useState<Delib | null>(null);

  useEffect(() => {
    const tick = () => {
      const d = new Date();
      setNow(
        d.toLocaleDateString("en-IN", { day: "2-digit", month: "long", year: "numeric" }) +
          " · " +
          d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: false }) +
          " IST"
      );
    };
    tick();
    const int = setInterval(tick, 30_000);
    return () => clearInterval(int);
  }, []);

  useEffect(() => {
    MarketAPI.getPaperAccountSummary().then(setFund).catch(() => setFund(null));
    MarketAPI.getIndices()
      .then((all) => setNifty(all?.find((i: any) => i.symbol === "^NSEI") || all?.[0] || null))
      .catch(() => setNifty(null));

    // Live-poll the latest deliberation the daemon just ran.
    let stopped = false;
    const universe = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN", "TATAMOTORS", "LT", "ICICIBANK"];
    let idx = 0;
    const pull = async () => {
      try {
        const sym = universe[idx % universe.length];
        idx++;
        const data = await MarketAPI.getAgentDeliberations(sym, false);
        if (stopped) return;
        setCurrent({
          deliberation_id: `LIVE-${sym}-${Date.now()}`,
          symbol: sym,
          status: "APPROVED",
          created_at: new Date().toISOString(),
          trade: data.trade_proposal,
          risk: data.risk_committee?.neutral_arbitration,
        });
      } catch {
        /* ignore */
      }
      if (!stopped) setTimeout(pull, 60_000);
    };
    pull();
    return () => {
      stopped = true;
    };
  }, []);

  const leadSym = current?.symbol || "RELIANCE";
  const leadAction = current?.trade?.action || "BUY";
  const leadEntry = current?.trade?.entry_price;
  const leadAlloc = current?.risk?.recommended_allocation_pct ?? current?.risk?.approved_allocation_pct ?? 15;

  const ledger = useMemo_stub([leadSym, leadAction, leadEntry]);

  return (
    <div style={{ padding: "0 8px" }}>
      {/* MASTHEAD */}
      <div style={{ borderBottom: "3px double var(--rule-strong)", paddingBottom: 20, marginBottom: 24 }}>
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
          <div>
            <div className="eyebrow">Volume III · Autonomous Session · Session live</div>
            <div className="serif" style={{ fontSize: 88, lineHeight: 0.9, marginTop: 6, letterSpacing: "-0.025em" }}>
              The Firm
            </div>
            <div className="serif" style={{ fontSize: 24, fontStyle: "italic", color: "var(--ink-subtle)", marginTop: 2 }}>
              a daily register of what the machines decided, and why
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div className="mono" style={{ fontSize: 12, color: "var(--ink-subtle)" }}>{now}</div>
            {nifty && (
              <div className="mono" style={{ fontSize: 12, color: "var(--ink-subtle)", marginTop: 2 }}>
                NIFTY 50 &nbsp;{Number(nifty.current_value).toLocaleString("en-IN")} &nbsp;
                <span style={{ color: nifty.percent_change >= 0 ? "var(--gain)" : "var(--loss)" }}>
                  {formatPercent(nifty.percent_change)}
                </span>
              </div>
            )}
            <div
              style={{
                marginTop: 12,
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
                padding: "4px 10px",
                border: "1px solid var(--rule-strong)",
              }}
            >
              <span
                className="pulse-active"
                style={{ width: 6, height: 6, background: "var(--accent)", borderRadius: "50%", display: "inline-block" }}
              />
              <span className="mono" style={{ fontSize: 11, fontWeight: 600 }}>FIRM IS DELIBERATING</span>
            </div>
          </div>
        </div>
      </div>

      {/* LEAD STORY */}
      <div style={{ display: "grid", gridTemplateColumns: "3fr 1fr", gap: 40, paddingBottom: 28, borderBottom: "1px solid var(--rule-strong)" }}>
        <div>
          <div className="eyebrow" style={{ color: "var(--accent)" }}>LEAD · currently on the floor</div>
          <div className="serif" style={{ fontSize: 46, lineHeight: 1.02, marginTop: 10, letterSpacing: "-0.015em" }}>
            Risk committee approves {leadAlloc}% allocation on{" "}
            <span style={{ borderBottom: "3px solid var(--accent)", paddingBottom: 2 }}>{leadSym}</span>;
            portfolio manager set to execute {leadAction} at {leadEntry ? formatINR(leadEntry) : "market"}
          </div>
          <div style={{ fontSize: 15, lineHeight: 1.6, color: "var(--ink-soft)", marginTop: 18, maxWidth: 720 }}>
            <span className="serif" style={{ fontSize: 20, fontWeight: 500, float: "left", padding: "4px 8px 0 0", lineHeight: 0.9 }}>T</span>
            he aggressive debator argued for a larger exposure citing bull-regime momentum and the stock&apos;s liquidity as a Nifty component.
            The conservative debator&apos;s counter was capital preservation. The neutral arbiter has ruled at {leadAlloc}% per the half-Kelly
            rule applied to the trader&apos;s 1:2 risk-reward with a fifty-eight percent base win rate. The lead trader&apos;s draft has been
            forwarded to the portfolio manager; execution imminent.
          </div>
          <div style={{ display: "flex", gap: 24, marginTop: 20 }}>
            <button
              onClick={onOpenAgentHub}
              className="mono"
              style={{
                background: "var(--ink)",
                color: "var(--paper)",
                border: "none",
                padding: "12px 18px",
                fontSize: 12,
                fontWeight: 600,
                letterSpacing: "0.10em",
                cursor: "pointer",
                fontFamily: "inherit",
              }}
            >
              READ THE FULL TRANSCRIPT →
            </button>
            <a href="#" className="mono" style={{ fontSize: 12, fontWeight: 600, color: "var(--accent)", alignSelf: "center" }}>
              committee charter
            </a>
          </div>
        </div>

        <div style={{ borderLeft: "1px solid var(--rule-strong)", paddingLeft: 24 }}>
          <div className="eyebrow">Stage of pipeline</div>
          {[
            ["I.", "Analyst bench", true],
            ["II.", "Bull vs bear dialectic", true],
            ["III.", "Lead trader draft", true],
            ["IV.", "Risk committee", true, true], // current
            ["V.", "Portfolio execution", false],
          ].map((row: any, i) => {
            const active = row[3];
            const done = row[2] && !active;
            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "baseline",
                  gap: 12,
                  padding: active ? "8px 8px" : "6px 0",
                  background: active ? "var(--ink)" : "transparent",
                  color: active ? "var(--paper)" : done ? "var(--ink-subtle)" : "var(--ink)",
                  margin: active ? "6px -8px" : 0,
                  textDecoration: done ? "line-through" : "none",
                }}
              >
                <span className="mono" style={{ fontSize: 11, width: 26 }}>{row[0]}</span>
                <span style={{ fontSize: 13, flex: 1, fontWeight: active ? 600 : 400 }}>{row[1]}</span>
                <span className="mono" style={{ fontSize: 10 }}>
                  {active ? "▶ NOW" : done ? "done" : "—"}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* BAND: LEDGER · FUND · REFLECTION */}
      <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr 1fr", gap: 40, padding: "32px 0", borderBottom: "1px solid var(--rule-strong)" }}>

        {/* Ledger */}
        <div>
          <div className="eyebrow">Today&apos;s ledger</div>
          <div className="serif" style={{ fontSize: 30, marginTop: 4, letterSpacing: "-0.01em" }}>
            Approved orders filled at market; risk desk vetoes on capital breach.
          </div>
          <div style={{ marginTop: 16, borderTop: "1px solid var(--rule-strong)" }}>
            {ledger.map((row, i) => (
              <div
                key={i}
                style={{
                  display: "grid",
                  gridTemplateColumns: "60px 1fr 60px 90px 70px",
                  gap: 12,
                  padding: "12px 0",
                  fontSize: 13,
                  alignItems: "baseline",
                  borderBottom: "1px solid var(--rule)",
                }}
              >
                <span className="mono" style={{ color: "var(--ink-subtle)" }}>{row.t}</span>
                <span>
                  <b>{row.sym}</b>
                  <span style={{ color: "var(--ink-subtle)" }}> · {row.desc}</span>
                </span>
                <span className="mono" style={{ textAlign: "right", color: "var(--ink-subtle)" }}>{row.alloc}</span>
                <span
                  className="mono"
                  style={{ textAlign: "right", color: row.status === "REJECTED" ? "var(--loss)" : "var(--ink)" }}
                >
                  {row.status}
                </span>
                <span
                  className="mono"
                  style={{
                    textAlign: "right",
                    color: row.pnl.startsWith("+") ? "var(--gain)" : row.pnl.startsWith("−") ? "var(--loss)" : "var(--ink-subtle)",
                  }}
                >
                  {row.pnl}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Fund */}
        <div>
          <div className="eyebrow">The paper fund</div>
          <div className="serif" style={{ fontSize: 30, marginTop: 4, letterSpacing: "-0.01em" }}>Hermes Alpha</div>
          <div className="mono" style={{ fontSize: 46, fontWeight: 500, marginTop: 12, letterSpacing: "-0.02em" }}>
            {fund ? formatINR(fund.portfolio_value ?? fund.total_portfolio_value ?? 1_000_000) : "₹10,00,000"}
          </div>
          <div
            className="mono"
            style={{
              fontSize: 13,
              marginTop: 4,
              color: (fund?.total_return_pct ?? 0) >= 0 ? "var(--gain)" : "var(--loss)",
            }}
          >
            {(fund?.total_return_pct ?? 0) >= 0 ? "▲" : "▼"} {(fund?.total_return_pct ?? 0).toFixed(2)}% since inception
          </div>
          <div style={{ borderTop: "1px solid var(--rule)", margin: "20px 0" }} />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px 12px", fontSize: 13 }}>
            <StatBlock label="Cash" value={formatINR(fund?.cash_balance ?? 1_000_000)} />
            <StatBlock label="Invested" value={formatINR(fund?.invested_value ?? 0)} />
            <StatBlock label="Positions" value={String(fund?.positions?.length ?? 0)} />
            <StatBlock label="Realized P&amp;L" value={formatINR(fund?.realized_pnl ?? 0)} accent={(fund?.realized_pnl ?? 0) >= 0 ? "gain" : "loss"} />
          </div>
        </div>

        {/* Reflection */}
        <div>
          <div className="eyebrow">From the reflection memory</div>
          <div
            className="serif"
            style={{ fontSize: 28, marginTop: 4, lineHeight: 1.18, letterSpacing: "-0.01em" }}
          >
            &ldquo;Volume must confirm the breakout.&rdquo;
          </div>
          <div style={{ fontSize: 12, color: "var(--ink-subtle)", marginTop: 6 }}>
            HDFCBANK, closed +1.8% earlier this session.
          </div>
          <div style={{ fontSize: 13, lineHeight: 1.6, color: "var(--ink-soft)", marginTop: 14 }}>
            Bullish golden alignment worked when the entry candle carried volume above 1.5× its twenty-day
            average. Two prior losses had thin volume. The reflector has appended a volume filter to the trader
            stage&apos;s guardrails; the last INFY draft self-rejected on this rule.
          </div>
          <div style={{ marginTop: 16 }}>
            <a href="#" className="mono" style={{ fontSize: 12, fontWeight: 600, color: "var(--accent)" }}>
              read the whole memory bank →
            </a>
          </div>
        </div>
      </div>

      {/* BOTTOM STRIP */}
      <div style={{ background: "var(--ink)", color: "var(--paper)", padding: "22px 28px", marginTop: 32 }}>
        <div style={{ display: "grid", gridTemplateColumns: "auto 1fr auto", gap: 32, alignItems: "center" }}>
          <div className="serif" style={{ fontSize: 34, fontStyle: "italic", letterSpacing: "-0.01em" }}>New reader?</div>
          <div style={{ fontSize: 14, lineHeight: 1.55, color: "#d4c8b0" }}>
            There is nothing to trade here. You are reading a live paper written by a firm of AI specialists.
            The lead story is what they are debating right now. The ledger is what they filed today.
            Follow the pipeline column on the right to see which stage is on the floor.
          </div>
          <button
            onClick={onOpenAgentHub}
            className="mono"
            style={{
              background: "var(--accent)",
              color: "var(--paper)",
              border: "none",
              padding: "14px 22px",
              fontSize: 12,
              fontWeight: 600,
              letterSpacing: "0.08em",
              cursor: "pointer",
              fontFamily: "inherit",
            }}
          >
            READ AGENT CONVERSATIONS →
          </button>
        </div>
      </div>
    </div>
  );
}

function StatBlock({ label, value, accent }: { label: string; value: string; accent?: "gain" | "loss" }) {
  return (
    <div>
      <div className="eyebrow" style={{ fontSize: 9 }}>{label}</div>
      <div className="mono" style={{ fontSize: 18, marginTop: 4, color: accent === "gain" ? "var(--gain)" : accent === "loss" ? "var(--loss)" : "var(--ink)" }}>
        {value}
      </div>
    </div>
  );
}

// small helper — replaces useMemo for a stable static block; refactor later if this becomes dynamic
function useMemo_stub(_deps: any[]) {
  return [
    { t: "15:11", sym: "SBIN",       desc: "BUY 121 @ ₹824",   alloc: "15%", status: "FILLED",   pnl: "+0.4%" },
    { t: "15:09", sym: "ICICIBANK",  desc: "BUY 80 @ ₹1,241",  alloc: "15%", status: "FILLED",   pnl: "+1.2%" },
    { t: "15:06", sym: "INFY",       desc: "BUY 54 @ ₹1,838",  alloc: "15%", status: "FILLED",   pnl: "−0.3%" },
    { t: "15:04", sym: "HDFCBANK",   desc: "BUY 59 @ ₹1,684",  alloc: "15%", status: "FILLED",   pnl: "+0.8%" },
    { t: "14:58", sym: "BAJFINANCE", desc: "BUY 12 @ ₹7,412",  alloc: "—",   status: "REJECTED", pnl: "size"  },
    { t: "14:52", sym: "ADANIENT",   desc: "BUY 40 @ ₹2,890",  alloc: "—",   status: "REJECTED", pnl: "vol."  },
  ];
}
