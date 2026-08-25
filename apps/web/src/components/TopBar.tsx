"use client";

import React, { useState, useEffect } from "react";
import { Clock, Radio, Activity, AlertCircle, RefreshCw } from "lucide-react";
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

export function TopBar({ 
  status, 
  indices, 
  isConnected, 
  onRefresh,
  onOpenTelegram,
  onOpenAvatar,
  onOpenSkills
}: TopBarProps) {
  const [istTime, setIstTime] = useState<string>("");

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      // Format to IST
      const options: Intl.DateTimeFormatOptions = {
        timeZone: "Asia/Kolkata",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false,
      };
      const timeStr = new Intl.DateTimeFormat("en-GB", options).format(now);
      const dateStr = new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Kolkata", day: "2-digit", month: "short", year: "numeric" }).format(now);
      setIstTime(`${dateStr} ${timeStr} IST`);
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  const getStatusBadge = () => {
    if (!status) return null;
    const isTrading = status.status === "OPEN" || status.status === "SPECIAL_SESSION";
    const isPre = status.status === "PRE_OPEN";
    
    if (isTrading) {
      return (
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold font-mono">
          <span className="w-2 h-2 rounded-full bg-emerald-400 pulse-active shadow-glow-green" />
          <span>MARKET LIVE</span>
        </div>
      );
    }

    if (isPre) {
      return (
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-semibold font-mono">
          <span className="w-2 h-2 rounded-full bg-amber-400 pulse-active" />
          <span>PRE-OPEN</span>
        </div>
      );
    }

    return (
      <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold font-mono">
        <span className="w-2 h-2 rounded-full bg-rose-400" />
        <span>CLOSED ({status.status})</span>
      </div>
    );
  };

  return (
    <header className="h-16 border-b border-[#1e293b] bg-[#090d16]/90 backdrop-blur-md px-6 flex items-center justify-between shrink-0 z-20">
      {/* Left: Market Status & Live Clock */}
      <div className="flex items-center gap-4">
        {getStatusBadge()}

        <div className="flex items-center gap-2 text-xs font-mono text-[#94a3b8] bg-[#0e131f] px-3 py-1 rounded border border-[#1e293b]">
          <Clock className="w-3.5 h-3.5 text-cyan-400" />
          <span>{istTime || "Loading IST..."}</span>
        </div>
      </div>

      {/* Center: Live Scrolling Ticker Ribbon */}
      <div className="hidden lg:flex items-center gap-6 overflow-hidden max-w-2xl">
        {indices.map((idx) => {
          const isUp = idx.change >= 0;
          return (
            <div key={idx.symbol} className="flex items-center gap-2 text-xs shrink-0 font-mono">
              <span className="text-[#64748b] font-semibold">{idx.symbol}</span>
              <span className="text-white font-medium">{formatNumber(idx.current_value)}</span>
              <span className={`font-semibold ${isUp ? "text-emerald-400" : "text-rose-400"}`}>
                {formatPercent(idx.percent_change)}
              </span>
            </div>
          );
        })}
      </div>

      {/* Right: Quick Action Launchers & Live Status */}
      <div className="flex items-center gap-3">
        {onOpenTelegram && (
          <button
            onClick={onOpenTelegram}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#0284c7]/20 hover:bg-[#0284c7]/30 text-sky-400 border border-sky-500/30 text-xs font-medium transition"
            title="Open Telegram Alert Bot"
          >
            <Send className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Telegram Bot</span>
          </button>
        )}

        {onOpenAvatar && (
          <button
            onClick={onOpenAvatar}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#a855f7]/20 hover:bg-[#a855f7]/30 text-purple-400 border border-purple-500/30 text-xs font-medium transition"
            title="Open Talking Avatar Studio"
          >
            <Video className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Avatar Studio</span>
          </button>
        )}

        {onOpenSkills && (
          <button
            onClick={onOpenSkills}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#eab308]/20 hover:bg-[#eab308]/30 text-amber-400 border border-amber-500/30 text-xs font-medium transition"
            title="Open Hermes Skills Matrix"
          >
            <Zap className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Skills Matrix</span>
          </button>
        )}

        <div className="flex items-center gap-1.5 text-[11px] font-mono text-[#64748b] ml-2">
          <Radio className={`w-3.5 h-3.5 ${isConnected ? "text-emerald-400 pulse-active" : "text-amber-400"}`} />
          <span>{isConnected ? "WS STREAM" : "HTTP"}</span>
        </div>

        <button
          onClick={onRefresh}
          className="p-1.5 rounded bg-[#151b2c] hover:bg-[#1e293b] text-[#94a3b8] hover:text-white border border-[#1e293b] transition"
          title="Refresh Data"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>
    </header>
  );
}
