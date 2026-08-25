"use client";

import React, { useState, useEffect } from "react";
import { Activity, RefreshCw, Zap, TrendingUp, TrendingDown, Target, Shield } from "lucide-react";
import { MarketAPI } from "@/lib/api";
import { formatINR, formatNumber, formatPercent } from "@/lib/utils";

export function DerivativesView() {
  const [symbol, setSymbol] = useState<string>("NIFTY 50");
  const [fnoList, setFnoList] = useState<any[]>([]);
  const [chain, setChain] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    MarketAPI.getFnoUniverse().then(setFnoList).catch(console.error);
  }, []);

  const loadChain = async (sym: string) => {
    setLoading(true);
    try {
      const data = await MarketAPI.getOptionChain(sym, 17);
      setChain(data);
    } catch (err) {
      console.error("Error loading option chain:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadChain(symbol);
  }, [symbol]);

  const maxOI = chain
    ? Math.max(
        ...chain.strikes.map((s: any) => Math.max(s.call.open_interest, s.put.open_interest)),
        1
      )
    : 1;

  return (
    <div className="space-y-5">
      {/* Top Controls & Asset Selector */}
      <div className="terminal-card p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400" />
            <h2 className="text-base font-bold font-mono text-white">
              F&O OPTION CHAIN & DERIVATIVES LADDER
            </h2>
          </div>
          <div className="text-xs text-[#64748b] font-mono mt-0.5">
            Real-time Black-Scholes Greeks, Open Interest (OI) Analysis & Max Pain
          </div>
        </div>

        <div className="flex items-center gap-3 font-mono text-xs">
          <div className="flex items-center gap-2">
            <span className="text-[#64748b]">Underlying:</span>
            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="bg-[#090d16] border border-[#1e293b] rounded px-3 py-1.5 text-white focus:outline-none focus:border-cyan-500 font-mono"
            >
              {fnoList.map((f) => (
                <option key={f.symbol} value={f.symbol}>
                  {f.symbol} ({f.type})
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={() => loadChain(symbol)}
            className="p-2 rounded bg-[#151b2c] hover:bg-[#1e293b] text-[#94a3b8] hover:text-white border border-[#1e293b] transition"
            title="Refresh Option Chain"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-cyan-400" : ""}`} />
          </button>
        </div>
      </div>

      {/* Metrics Summary Banner */}
      {chain && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 font-mono">
          <div className="bg-[#090d16] p-3.5 rounded-lg border border-[#1e293b]">
            <div className="text-[11px] text-[#64748b]">Spot Price</div>
            <div className="text-lg font-bold text-white mt-1">{formatINR(chain.spot_price)}</div>
          </div>
          <div className="bg-[#090d16] p-3.5 rounded-lg border border-[#1e293b]">
            <div className="text-[11px] text-[#64748b]">Max Pain Strike</div>
            <div className="text-lg font-bold text-amber-400 mt-1">{formatNumber(chain.max_pain)}</div>
          </div>
          <div className="bg-[#090d16] p-3.5 rounded-lg border border-[#1e293b]">
            <div className="text-[11px] text-[#64748b]">Put-Call Ratio (OI)</div>
            <div
              className={`text-lg font-bold mt-1 ${
                chain.pcr_oi > 1.1 ? "text-emerald-400" : chain.pcr_oi < 0.85 ? "text-rose-400" : "text-cyan-400"
              }`}
            >
              {chain.pcr_oi} ({chain.sentiment})
            </div>
          </div>
          <div className="bg-[#090d16] p-3.5 rounded-lg border border-[#1e293b]">
            <div className="text-[11px] text-[#64748b]">Expiry Date</div>
            <div className="text-lg font-bold text-white mt-1">
              {chain.expiry_date} ({chain.days_to_expiry}d)
            </div>
          </div>
        </div>
      )}

      {/* Option Chain Table */}
      <div className="terminal-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs font-mono text-left">
            <thead>
              <tr className="bg-[#090d16] border-b border-[#1e293b] text-[#64748b]">
                <th colSpan={5} className="py-2.5 px-4 text-center bg-cyan-950/20 text-cyan-400 border-r border-[#1e293b]">
                  CALLS (CE)
                </th>
                <th className="py-2.5 px-4 text-center bg-[#070a10] text-white">STRIKE</th>
                <th colSpan={5} className="py-2.5 px-4 text-center bg-rose-950/20 text-rose-400 border-l border-[#1e293b]">
                  PUTS (PE)
                </th>
              </tr>
              <tr className="bg-[#0b101c] border-b border-[#1e293b] text-[11px] text-[#64748b]">
                <th className="py-2 px-3 text-right">OI (Shares)</th>
                <th className="py-2 px-3 text-right">IV (%)</th>
                <th className="py-2 px-3 text-right">Delta</th>
                <th className="py-2 px-3 text-right">LTP (₹)</th>
                <th className="py-2 px-3 text-left border-r border-[#1e293b]">Build-up</th>
                
                <th className="py-2 px-4 text-center bg-[#090d16] text-white font-bold">PRICE</th>

                <th className="py-2 px-3 text-left border-l border-[#1e293b]">Build-up</th>
                <th className="py-2 px-3 text-right">LTP (₹)</th>
                <th className="py-2 px-3 text-right">Delta</th>
                <th className="py-2 px-3 text-right">IV (%)</th>
                <th className="py-2 px-3 text-right">OI (Shares)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e293b]/50">
              {loading ? (
                <tr>
                  <td colSpan={11} className="py-12 text-center text-cyan-400">
                    Computing Option Chain & Black-Scholes Greeks...
                  </td>
                </tr>
              ) : (
                chain?.strikes?.map((row: any) => {
                  const ceBarPct = Math.min(100, Math.round((row.call.open_interest / maxOI) * 100));
                  const peBarPct = Math.min(100, Math.round((row.put.open_interest / maxOI) * 100));

                  return (
                    <tr
                      key={row.strike_price}
                      className={`hover:bg-[#131929] transition ${
                        row.is_atm ? "bg-cyan-500/10 font-bold border-y border-cyan-500/40" : ""
                      }`}
                    >
                      {/* CALL SIDE */}
                      <td className="py-2 px-3 text-right relative">
                        <div
                          className="absolute right-0 top-1 bottom-1 bg-cyan-500/15 rounded-l"
                          style={{ width: `${ceBarPct}%` }}
                        />
                        <span className="relative z-10 text-white font-semibold">
                          {formatNumber(row.call.open_interest)}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-right text-[#94a3b8]">{row.call.iv}%</td>
                      <td className="py-2 px-3 text-right text-cyan-400">{row.call.delta}</td>
                      <td className="py-2 px-3 text-right font-bold text-white">₹{row.call.ltp}</td>
                      <td className="py-2 px-3 text-left border-r border-[#1e293b]">
                        <span
                          className={`px-1.5 py-0.5 rounded text-[9px] ${
                            row.call.buildup === "Long Build-up"
                              ? "bg-emerald-500/10 text-emerald-400"
                              : "bg-rose-500/10 text-rose-400"
                          }`}
                        >
                          {row.call.buildup}
                        </span>
                      </td>

                      {/* STRIKE CENTER */}
                      <td className="py-2 px-4 text-center font-bold bg-[#090d16] text-white">
                        <span className={row.is_atm ? "text-cyan-400 underline decoration-cyan-400" : ""}>
                          {row.strike_price}
                        </span>
                        {row.is_atm && (
                          <span className="ml-1 text-[9px] px-1 py-0.2 bg-cyan-500 text-black rounded font-black">
                            ATM
                          </span>
                        )}
                      </td>

                      {/* PUT SIDE */}
                      <td className="py-2 px-3 text-left border-l border-[#1e293b]">
                        <span
                          className={`px-1.5 py-0.5 rounded text-[9px] ${
                            row.put.buildup === "Short Covering"
                              ? "bg-emerald-500/10 text-emerald-400"
                              : "bg-rose-500/10 text-rose-400"
                          }`}
                        >
                          {row.put.buildup}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-right font-bold text-white">₹{row.put.ltp}</td>
                      <td className="py-2 px-3 text-right text-rose-400">{row.put.delta}</td>
                      <td className="py-2 px-3 text-right text-[#94a3b8]">{row.put.iv}%</td>
                      <td className="py-2 px-3 text-right relative">
                        <div
                          className="absolute left-0 top-1 bottom-1 bg-rose-500/15 rounded-r"
                          style={{ width: `${peBarPct}%` }}
                        />
                        <span className="relative z-10 text-white font-semibold">
                          {formatNumber(row.put.open_interest)}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
