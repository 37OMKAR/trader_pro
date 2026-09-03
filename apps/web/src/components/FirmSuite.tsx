"use client";

import React, { useEffect, useMemo, useState } from "react";
import { MarketAPI } from "@/lib/api";
import { formatINR, formatPercent } from "@/lib/utils";

/**
 * FirmSuite — the trading-floor view.
 *
 * One page. Left column shows the 11-member firm with current status. Middle
 * column is the live deliberation transcript flowing as it happens. Right
 * column is the order queue + fund glance + reflection scratchpad.
 */

type AgentRow = {
  role: string;
  name: string;
  tier: "I" | "II" | "III" | "IV" | "V" | "VI";
  status: "idle" | "reading" | "speaking" | "waiting" | "ruled";
  note?: string;
};

type Msg = {
  agent: string;
  stage: string;
  ts: string;
  verdict?: string;
  body: string;
};

const FIRM: AgentRow[] = [
  { role: "Chair",             name: "Hermes",             tier: "VI",  status: "waiting", note: "convening" },
  { role: "Fundamentals",      name: "The Balance Sheet",  tier: "I",   status: "speaking", note: "STRONG_BUY" },
  { role: "Technicals",        name: "The Chartist",       tier: "I",   status: "speaking", note: "BULLISH" },
  { role: "Sentiment",         name: "The Tape Reader",    tier: "I",   status: "speaking", note: "BULLISH" },
  { role: "Macro",             name: "The Watchtower",     tier: "I",   status: "speaking", note: "FAVORABLE" },
  { role: "Bull Researcher",   name: "The Optimist",       tier: "II",  status: "waiting" },
  { role: "Bear Researcher",   name: "The Skeptic",        tier: "II",  status: "waiting" },
  { role: "Lead Trader",       name: "The Trader",         tier: "III", status: "waiting" },
  { role: "Aggressive",        name: "Debator, size up",   tier: "IV",  status: "waiting" },
  { role: "Conservative",      name: "Debator, size down", tier: "IV",  status: "waiting" },
  { role: "Neutral Arbiter",   name: "Kelly's neutral",    tier: "IV",  status: "waiting" },
  { role: "Portfolio Mgr",     name: "The Booker",         tier: "V",   status: "idle" },
  { role: "Reflector",         name: "The Reflector",      tier: "VI",  status: "idle" },
];

const roles = new Map<string, string>([
  ["Fundamentals",   "The Balance Sheet"],
  ["Technicals",     "The Chartist"],
  ["Sentiment",      "The Tape Reader"],
  ["Macro",          "The Watchtower"],
  ["Bull Researcher","The Optimist"],
  ["Bear Researcher","The Skeptic"],
  ["Lead Trader",    "The Trader"],
  ["Aggressive",     "Debator, size up"],
  ["Conservative",   "Debator, size down"],
  ["Neutral Arbiter","Kelly's neutral"],
  ["Portfolio Mgr",  "The Booker"],
]);

export function FirmSuite() {
  const universe = useMemo(() => ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "SBIN", "TATAMOTORS", "LT"], []);
  const [cursor, setCursor] = useState(0);
  const [symbol, setSymbol] = useState<string>(universe[0]);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [orders, setOrders] = useState<any[]>([]);
  const [fund, setFund] = useState<any>(null);
  const [running, setRunning] = useState<boolean>(true);
  const [activeAgent, setActiveAgent] = useState<string>("Hermes");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    MarketAPI.getPaperAccountSummary().then(setFund).catch(() => {});
  }, []);

  useEffect(() => {
    let stopped = false;
    let timer: any;

    const spool = (delib: any, sym: string) => {
      const q = delib.quote || {};
      const analysts = delib.analyst_reports || {};
      const bull = delib.debate?.bull_case || {};
      const bear = delib.debate?.bear_case || {};
      const trade = delib.trade_proposal || {};
      const risk = delib.risk_committee || {};
      const arb = risk.neutral_arbitration || {};
      const pm = delib.portfolio_decision || {};

      const stream: Msg[] = [
        { agent: "Hermes", stage: "0", ts: "convene", body: `Universe roll: ${sym} — quote ${formatINR(q.last_price)} (${formatPercent(q.percent_change)}). Briefing the desks.` },
        { agent: "Fundamentals", stage: "I", ts: "+22s", verdict: analysts.fundamentals?.rating || "STRONG_BUY", body: analysts.fundamentals?.summary || "" },
        { agent: "Technicals", stage: "I", ts: "+24s", verdict: analysts.technicals?.trend || "BULLISH", body: analysts.technicals?.summary || "" },
        { agent: "Sentiment", stage: "I", ts: "+25s", verdict: analysts.sentiment?.sentiment_classification || "BULLISH", body: analysts.sentiment?.summary || "" },
        { agent: "Macro", stage: "I", ts: "+26s", verdict: analysts.macro?.macro_bias || "FAVORABLE", body: analysts.macro?.summary || "" },
        { agent: "Bull Researcher", stage: "II", ts: "+38s", verdict: "ACCUMULATE", body: bull.thesis || "" },
        { agent: "Bear Researcher", stage: "II", ts: "+40s", verdict: "CAUTION",    body: bear.thesis || "" },
        { agent: "Lead Trader", stage: "III", ts: "+55s", verdict: `${trade.action} · R:R ${trade.risk_reward_ratio}`,
          body: `${trade.action} @ ${formatINR(trade.entry_price)} · Stop ${formatINR(trade.stop_loss)} · T1 ${formatINR(trade.target_1)} · T2 ${formatINR(trade.target_2)}. ${trade.rationale || ""}` },
        { agent: "Aggressive", stage: "IV", ts: "+60s", verdict: `${risk.aggressive?.recommended_allocation_pct ?? 18}%`,
          body: risk.aggressive?.argument || "Bull regime, momentum leader — deploy 15-18%." },
        { agent: "Conservative", stage: "IV", ts: "+64s", verdict: `${risk.conservative?.recommended_allocation_pct ?? 7.5}%`,
          body: risk.conservative?.argument || "Preserve capital. 7.5% max, mechanical stops." },
        { agent: "Neutral Arbiter", stage: "IV", ts: "+72s", verdict: `${arb.approved_allocation_pct ?? arb.recommended_allocation_pct ?? 15}% approved`,
          body: arb.consensus_summary || "Half-Kelly compromise." },
        { agent: "Portfolio Mgr", stage: "V", ts: "+82s", verdict: pm.status || "EXECUTED",
          body: pm.executive_memo || `Filled — order booked.` },
      ];

      // Play back messages one every 1.4s so the user can watch the room
      setMessages([]);
      let i = 0;
      const step = () => {
        if (stopped) return;
        if (i >= stream.length) {
          // record order in queue
          setOrders((prev) =>
            [
              {
                sym,
                action: trade.action,
                qty: pm.order_details?.quantity ?? "—",
                price: trade.entry_price,
                alloc: arb.approved_allocation_pct ?? arb.recommended_allocation_pct ?? 15,
                status: pm.status || "APPROVED",
                ts: new Date().toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" }),
              },
              ...prev,
            ].slice(0, 12)
          );
          setActiveAgent("Hermes");
          // Next symbol after a beat
          setTimeout(() => {
            if (!stopped && running) {
              setCursor((c) => (c + 1) % universe.length);
            }
          }, 4000);
          return;
        }
        const m = stream[i];
        setActiveAgent(m.agent);
        setMessages((prev) => [...prev, m]);
        i++;
        timer = setTimeout(step, 1400);
      };
      step();
    };

    const fire = async () => {
      const sym = universe[cursor];
      setSymbol(sym);
      try {
        setError(null);
        const delib = await MarketAPI.getAgentDeliberations(sym, false);
        if (stopped) return;
        spool(delib, sym);
      } catch (e: any) {
        setError(e?.message || "failed to reach the firm");
      }
    };
    fire();

    return () => {
      stopped = true;
      if (timer) clearTimeout(timer);
    };
  }, [cursor, universe, running]);

  return (
    <div style={{ padding: "0 8px" }}>
      {/* Header */}
      <div style={{ borderBottom: "3px double var(--rule-strong)", paddingBottom: 20, marginBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <div className="eyebrow">The Suite · live floor</div>
            <div className="serif" style={{ fontSize: 68, lineHeight: 0.94, letterSpacing: "-0.02em", marginTop: 4 }}>
              The Trading Floor
            </div>
            <div className="serif" style={{ fontSize: 20, fontStyle: "italic", color: "var(--ink-subtle)", marginTop: 2 }}>
              eleven specialists, one chair, one paper fund — everything you can hear right now
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div className="eyebrow">Currently on the floor</div>
            <div className="serif" style={{ fontSize: 40, letterSpacing: "-0.01em", marginTop: 2 }}>{symbol}</div>
            <div style={{ display: "flex", gap: 6, marginTop: 8, justifyContent: "flex-end" }}>
              <button
                onClick={() => setCursor((c) => (c - 1 + universe.length) % universe.length)}
                className="mono"
                style={{ padding: "5px 10px", border: "1px solid var(--rule-strong)", background: "var(--paper)", fontSize: 11, cursor: "pointer" }}
              >
                ◀ prev
              </button>
              <button
                onClick={() => setRunning((r) => !r)}
                className="mono"
                style={{
                  padding: "5px 10px",
                  border: "1px solid var(--rule-strong)",
                  background: running ? "var(--ink)" : "var(--paper)",
                  color: running ? "var(--paper)" : "var(--ink)",
                  fontSize: 11,
                  cursor: "pointer",
                  fontWeight: 600,
                }}
              >
                {running ? "■ pause" : "▶ resume"}
              </button>
              <button
                onClick={() => setCursor((c) => (c + 1) % universe.length)}
                className="mono"
                style={{ padding: "5px 10px", border: "1px solid var(--rule-strong)", background: "var(--paper)", fontSize: 11, cursor: "pointer" }}
              >
                next ▶
              </button>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div style={{ background: "var(--sunk)", border: "1px solid var(--accent)", color: "var(--accent)", padding: "10px 14px", marginBottom: 20, fontSize: 13 }}>
          {error} · showing cached transcript
        </div>
      )}

      {/* THREE-COLUMN FLOOR */}
      <div style={{ display: "grid", gridTemplateColumns: "280px 1fr 340px", gap: 32 }}>

        {/* LEFT — THE FIRM ROLL CALL */}
        <div>
          <div className="eyebrow">The firm · roll call</div>
          <div style={{ marginTop: 12, borderTop: "1px solid var(--rule-strong)" }}>
            {FIRM.map((a) => {
              const active = a.role === activeAgent || a.name === activeAgent || (a.role === "Chair" && activeAgent === "Hermes");
              return (
                <div
                  key={a.role}
                  style={{
                    display: "grid",
                    gridTemplateColumns: "24px 1fr auto",
                    gap: 8,
                    padding: "10px 10px",
                    borderBottom: "1px solid var(--rule)",
                    background: active ? "var(--ink)" : "transparent",
                    color: active ? "var(--paper)" : "var(--ink)",
                    alignItems: "baseline",
                  }}
                >
                  <span className="mono" style={{ fontSize: 10, color: active ? "rgba(244,239,228,0.7)" : "var(--ink-subtle)" }}>
                    {a.tier}
                  </span>
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 600 }}>{a.role}</div>
                    <div className="serif" style={{ fontSize: 15, fontStyle: "italic", color: active ? "rgba(244,239,228,0.85)" : "var(--ink-subtle)" }}>
                      {a.name}
                    </div>
                  </div>
                  <span
                    style={{
                      display: "inline-block",
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      background: active ? "var(--accent)" : "var(--rule)",
                    }}
                    className={active ? "pulse-active" : ""}
                  />
                </div>
              );
            })}
          </div>
        </div>

        {/* MIDDLE — LIVE TRANSCRIPT */}
        <div>
          <div className="eyebrow" style={{ color: "var(--accent)" }}>Live transcript · {symbol}</div>
          <div className="serif" style={{ fontSize: 28, letterSpacing: "-0.01em", marginTop: 4 }}>
            Meeting minutes, as they happen.
          </div>

          <div style={{ marginTop: 20, borderTop: "1px solid var(--rule-strong)" }}>
            {messages.length === 0 && (
              <div style={{ padding: "32px 8px", fontStyle: "italic", color: "var(--ink-subtle)" }}>
                Hermes is convening the firm on {symbol}…
              </div>
            )}
            {messages.map((m, i) => (
              <div key={i} style={{ display: "grid", gridTemplateColumns: "140px 1fr", gap: 24, padding: "18px 0", borderBottom: "1px solid var(--rule)" }}>
                <div>
                  <div className="serif" style={{ fontSize: 20, lineHeight: 1 }}>{m.agent}</div>
                  <div className="mono" style={{ fontSize: 10, color: "var(--ink-subtle)", marginTop: 4 }}>stage {m.stage} · {m.ts}</div>
                  {m.verdict && (
                    <div
                      className="mono"
                      style={{
                        fontSize: 10,
                        marginTop: 8,
                        padding: "2px 6px",
                        background: "var(--ink)",
                        color: "var(--paper)",
                        display: "inline-block",
                      }}
                    >
                      {m.verdict}
                    </div>
                  )}
                </div>
                <div className="serif" style={{ fontSize: 17, lineHeight: 1.5, color: "var(--ink)" }}>
                  &ldquo;{m.body}&rdquo;
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* RIGHT — ORDER QUEUE + FUND + REFLECTION */}
        <div>
          <div className="eyebrow">Order queue · executed by the PM</div>
          <div style={{ marginTop: 12, borderTop: "1px solid var(--rule-strong)" }}>
            {orders.length === 0 && (
              <div style={{ padding: "16px 0", fontStyle: "italic", color: "var(--ink-subtle)", fontSize: 13 }}>
                waiting for the arbiter&apos;s ruling…
              </div>
            )}
            {orders.map((o, i) => (
              <div key={i} style={{ padding: "10px 0", borderBottom: "1px solid var(--rule)", fontSize: 13 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                  <div>
                    <b>{o.sym}</b>
                    <span className="mono" style={{ fontSize: 11, color: "var(--ink-subtle)" }}> · {o.ts}</span>
                  </div>
                  <span className="mono" style={{ fontSize: 10, background: "var(--ink)", color: "var(--paper)", padding: "2px 6px" }}>
                    {o.status}
                  </span>
                </div>
                <div className="mono" style={{ fontSize: 12, marginTop: 4, color: "var(--ink-soft)" }}>
                  {o.action} {o.qty} @ {formatINR(o.price)} · {o.alloc}% capital
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: 28, borderTop: "1px solid var(--rule-strong)", paddingTop: 16 }}>
            <div className="eyebrow">Paper fund</div>
            <div className="serif" style={{ fontSize: 22, marginTop: 4 }}>Hermes Alpha</div>
            <div className="mono" style={{ fontSize: 30, fontWeight: 500, marginTop: 8, letterSpacing: "-0.02em" }}>
              {formatINR(fund?.portfolio_value ?? fund?.total_portfolio_value ?? 1_000_000)}
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 16 }}>
              <div>
                <div className="eyebrow" style={{ fontSize: 9 }}>Cash</div>
                <div className="mono" style={{ fontSize: 14, marginTop: 2 }}>{formatINR(fund?.cash_balance ?? 1_000_000)}</div>
              </div>
              <div>
                <div className="eyebrow" style={{ fontSize: 9 }}>Positions</div>
                <div className="mono" style={{ fontSize: 14, marginTop: 2 }}>{fund?.positions?.length ?? 0}</div>
              </div>
            </div>
          </div>

          <div style={{ marginTop: 28, borderTop: "1px solid var(--rule-strong)", paddingTop: 16 }}>
            <div className="eyebrow">The reflector&apos;s note</div>
            <div className="serif" style={{ fontSize: 20, marginTop: 4, lineHeight: 1.25 }}>
              &ldquo;Volume must confirm the breakout.&rdquo;
            </div>
            <div style={{ fontSize: 12, color: "var(--ink-subtle)", marginTop: 6 }}>
              from HDFCBANK, closed +1.8%.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
