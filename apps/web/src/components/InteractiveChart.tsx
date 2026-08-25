"use client";

import React, { useState } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  Bar,
  ComposedChart,
  Line,
  CartesianGrid,
} from "recharts";
import { Candle } from "@/types";
import { formatNumber } from "@/lib/utils";
import { Maximize2, BarChart2, Layers } from "lucide-react";

interface InteractiveChartProps {
  symbol: string;
  candles: Candle[];
  timeframe: string;
  setTimeframe: (tf: string) => void;
  isLoading: boolean;
}

export function InteractiveChart({
  symbol,
  candles,
  timeframe,
  setTimeframe,
  isLoading,
}: InteractiveChartProps) {
  const [showSMA, setShowSMA] = useState<boolean>(true);
  const timeframes = ["1m", "5m", "15m", "1h", "1D"];

  // Calculate Simple Moving Average (SMA 20)
  const chartData = candles.map((c, idx, arr) => {
    let sma20 = null;
    if (idx >= 19) {
      const slice = arr.slice(idx - 19, idx + 1);
      const sum = slice.reduce((acc, curr) => acc + curr.close, 0);
      sma20 = sum / 20;
    }

    const dateObj = new Date(c.timestamp);
    const dateLabel = timeframe === "1D" 
      ? dateObj.toLocaleDateString("en-IN", { month: "short", day: "numeric" })
      : dateObj.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });

    return {
      ...c,
      dateLabel,
      sma20,
    };
  });

  const minPrice = Math.min(...candles.map((c) => c.low || c.close)) * 0.998;
  const maxPrice = Math.max(...candles.map((c) => c.high || c.close)) * 1.002;

  return (
    <div className="terminal-card p-5 flex flex-col h-[460px]">
      {/* Chart Header Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b border-[#1e293b]">
        <div className="flex items-center gap-3">
          <span className="text-sm font-bold text-white font-mono tracking-wide">{symbol}</span>
          <span className="text-xs text-[#64748b] bg-[#151b2c] px-2 py-0.5 rounded font-mono">
            NSE CONTINUOUS
          </span>
        </div>

        <div className="flex items-center gap-3">
          {/* Moving Average Toggle */}
          <button
            onClick={() => setShowSMA(!showSMA)}
            className={`text-xs px-2.5 py-1 rounded font-mono flex items-center gap-1.5 transition ${
              showSMA
                ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                : "bg-[#151b2c] text-[#64748b] border border-[#1e293b]"
            }`}
          >
            <Layers className="w-3 h-3" />
            <span>SMA 20</span>
          </button>

          {/* Timeframe Switcher */}
          <div className="flex items-center bg-[#090d16] p-0.5 rounded border border-[#1e293b]">
            {timeframes.map((tf) => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`text-xs px-2.5 py-1 rounded font-mono transition ${
                  timeframe === tf
                    ? "bg-cyan-500 text-black font-bold shadow-sm"
                    : "text-[#64748b] hover:text-white"
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart Canvas */}
      <div className="flex-1 w-full min-h-[300px] relative">
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-[#0e131f]/60 backdrop-blur-sm z-10">
            <span className="text-xs font-mono text-cyan-400 animate-pulse">Loading Candlestick Data...</span>
          </div>
        ) : null}

        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
            <defs>
              <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00e5ff" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#00e5ff" stopOpacity={0.0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.6} />

            <XAxis
              dataKey="dateLabel"
              stroke="#64748b"
              fontSize={10}
              tickLine={false}
              axisLine={{ stroke: "#1e293b" }}
            />

            <YAxis
              domain={[minPrice, maxPrice]}
              orientation="right"
              stroke="#64748b"
              fontSize={10}
              tickLine={false}
              axisLine={{ stroke: "#1e293b" }}
              tickFormatter={(val) => formatNumber(val, 1)}
            />

            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload as Candle & { dateLabel: string; sma20?: number };
                  return (
                    <div className="bg-[#090d16] border border-[#1e293b] p-3 rounded shadow-glass font-mono text-xs space-y-1">
                      <div className="text-[#94a3b8] font-bold border-b border-[#1e293b] pb-1">
                        {data.dateLabel}
                      </div>
                      <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 pt-1">
                        <span className="text-[#64748b]">O: <span className="text-white">{formatNumber(data.open)}</span></span>
                        <span className="text-[#64748b]">H: <span className="text-white">{formatNumber(data.high)}</span></span>
                        <span className="text-[#64748b]">L: <span className="text-white">{formatNumber(data.low)}</span></span>
                        <span className="text-[#64748b]">C: <span className="text-cyan-400 font-bold">{formatNumber(data.close)}</span></span>
                      </div>
                      <div className="text-[#64748b] text-[10px] pt-1">
                        Vol: <span className="text-[#94a3b8]">{formatNumber(data.volume, 0)}</span>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />

            {/* Price Area */}
            <Area
              type="monotone"
              dataKey="close"
              stroke="#00e5ff"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#priceGradient)"
            />

            {/* Moving Average Line */}
            {showSMA && (
              <Line
                type="monotone"
                dataKey="sma20"
                stroke="#f59e0b"
                strokeWidth={1.5}
                dot={false}
                name="SMA 20"
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
