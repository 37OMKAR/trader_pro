"use client";

import React, { useState, useEffect } from "react";
import { RefreshCw } from "lucide-react";
import { MarketStatusResponse, IndexQuote } from "@/types";
import { formatNumber, formatPercent } from "@/lib/utils";

interface TopBarProps {
  status: MarketStatusResponse | null;
  indices: IndexQuote[];
  isConnected: boolean;
  onRefresh: () => void;
  onOpenTelegram?: () => void;
  onOpenAvatar?: () => void;
  onOpenSkills?: () => void;
}

export function TopBar({ status, indices, isConnected, onRefresh }: TopBarProps) {
  const [istTime, setIstTime] = useState<string>("");

  useEffect(() => {
    const update = () => {
      const now = new Date();
      const t = new Intl.DateTimeFormat("en-GB", {
        timeZone: "Asia/Kolkata",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false,
      }).format(now);
      const d = new Intl.DateTimeFormat("en-GB", {
        timeZone: "Asia/Kolkata",
        day: "2-digit",
        month: "short",
        year: "numeric",
      }).format(now);
      setIstTime(`${d} · ${t} IST`);
    };
    update();
    const i = setInterval(update, 1000);
    return () => clearInterval(i);
  }, []);

  const statusLabel = (() => {
    if (!status) return "…";
    if (status.status === "OPEN" || status.status === "SPECIAL_SESSION") return "MARKET OPEN";
    if (status.status === "PRE_OPEN") return "PRE-OPEN";
    return "CLOSED";
  })();

  return (
    <header
      style={{
        height: 56,
        borderBottom: "1px solid var(--rule-strong)",
        background: "var(--paper)",
        padding: "0 28px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexShrink: 0,
        zIndex: 20,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
        <div
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 8,
            padding: "3px 10px",
            border: "1px solid var(--rule-strong)",
          }}
        >
          <span
            className={statusLabel !== "CLOSED" ? "pulse-active" : ""}
            style={{
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: statusLabel === "MARKET OPEN" ? "var(--gain)" : statusLabel === "CLOSED" ? "var(--loss)" : "var(--accent)",
              display: "inline-block",
            }}
          />
          <span className="mono" style={{ fontSize: 11, fontWeight: 600, letterSpacing: "0.10em" }}>
            {statusLabel}
          </span>
        </div>
        <span className="mono" style={{ fontSize: 11, color: "var(--ink-subtle)" }}>{istTime}</span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 24, overflow: "hidden", maxWidth: 720 }}>
        {indices.slice(0, 4).map((idx) => {
          const up = idx.change >= 0;
          return (
            <div key={idx.symbol} className="mono" style={{ fontSize: 11, display: "flex", gap: 6, alignItems: "baseline", flexShrink: 0 }}>
              <span style={{ color: "var(--ink-subtle)", fontWeight: 600 }}>{idx.symbol}</span>
              <span style={{ color: "var(--ink)" }}>{formatNumber(idx.current_value)}</span>
              <span style={{ color: up ? "var(--gain)" : "var(--loss)", fontWeight: 600 }}>
                {formatPercent(idx.percent_change)}
              </span>
            </div>
          );
        })}
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <span className="mono" style={{ fontSize: 10, color: isConnected ? "var(--gain)" : "var(--ink-subtle)", letterSpacing: "0.10em" }}>
          {isConnected ? "WS · LIVE" : "HTTP"}
        </span>
        <button
          onClick={onRefresh}
          style={{
            padding: "6px 8px",
            background: "var(--paper)",
            border: "1px solid var(--rule-strong)",
            color: "var(--ink)",
            cursor: "pointer",
          }}
          title="Refresh"
        >
          <RefreshCw style={{ width: 14, height: 14 }} />
        </button>
      </div>
    </header>
  );
}
