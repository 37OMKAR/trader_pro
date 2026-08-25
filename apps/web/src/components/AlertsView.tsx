"use client";

import React, { useState, useEffect } from "react";
import { Bell, Plus, Trash2, AlertTriangle, CheckCircle, ShieldAlert } from "lucide-react";
import { MarketAPI } from "@/lib/api";

export function AlertsView() {
  const [rules, setRules] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [symbol, setSymbol] = useState<string>("RELIANCE");
  const [ruleType, setRuleType] = useState<string>("PRICE_ABOVE");
  const [threshold, setThreshold] = useState<number>(3000);
  const [message, setMessage] = useState<string>("Price crossed target.");
  const [loading, setLoading] = useState<boolean>(true);

  const loadAlerts = async () => {
    try {
      const [rData, hData] = await Promise.all([
        MarketAPI.getAlertRules(),
        MarketAPI.getAlertHistory(),
      ]);
      setRules(rData);
      setHistory(hData);
    } catch (err) {
      console.error("Error loading alerts:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await MarketAPI.createAlertRule({
        rule_id: `RULE_${Date.now()}`,
        symbol: symbol.toUpperCase(),
        rule_type: ruleType,
        threshold: Number(threshold),
        message: message,
        enabled: true,
      });
      await loadAlerts();
    } catch (err) {
      console.error("Error creating alert rule:", err);
    }
  };

  const handleDeleteRule = async (ruleId: string) => {
    try {
      await MarketAPI.deleteAlertRule(ruleId);
      await loadAlerts();
    } catch (err) {
      console.error("Error deleting rule:", err);
    }
  };

  return (
    <div className="space-y-6 font-mono text-xs">
      {/* Header */}
      <div className="terminal-card p-5 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-amber-400" />
            <h2 className="text-base font-bold text-white">DETERMINISTIC ALERT ENGINE</h2>
          </div>
          <div className="text-xs text-[#64748b] mt-0.5">
            Real-Time Threshold Crossings, RSI Divergence, and Portfolio Drawdown Sentinel
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Create Rule Form */}
        <div className="terminal-card p-5 space-y-4">
          <div className="text-white font-bold text-[11px] flex items-center gap-2">
            <Plus className="w-4 h-4 text-cyan-400" />
            <span>CREATE NEW ALERT RULE</span>
          </div>

          <form onSubmit={handleCreateRule} className="space-y-3">
            <div>
              <label className="text-[#64748b] text-[10px] block mb-1">ASSET SYMBOL</label>
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                className="w-full bg-[#090d16] border border-[#1e293b] rounded px-3 py-1.5 text-white font-mono"
                required
              />
            </div>

            <div>
              <label className="text-[#64748b] text-[10px] block mb-1">RULE CONDITION</label>
              <select
                value={ruleType}
                onChange={(e) => setRuleType(e.target.value)}
                className="w-full bg-[#090d16] border border-[#1e293b] rounded px-3 py-1.5 text-white font-mono"
              >
                <option value="PRICE_ABOVE">Price Above (₹)</option>
                <option value="PRICE_BELOW">Price Below (₹)</option>
                <option value="RSI_OVERSOLD">RSI Oversold (&lt; Threshold)</option>
                <option value="RSI_OVERBOUGHT">RSI Overbought (&gt; Threshold)</option>
                <option value="DRAWDOWN_BREACH">Max Drawdown Breach (%)</option>
              </select>
            </div>

            <div>
              <label className="text-[#64748b] text-[10px] block mb-1">TRIGGER THRESHOLD</label>
              <input
                type="number"
                step="0.1"
                value={threshold}
                onChange={(e) => setThreshold(Number(e.target.value))}
                className="w-full bg-[#090d16] border border-[#1e293b] rounded px-3 py-1.5 text-white font-mono"
                required
              />
            </div>

            <div>
              <label className="text-[#64748b] text-[10px] block mb-1">ALERT MESSAGE</label>
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="w-full bg-[#090d16] border border-[#1e293b] rounded px-3 py-1.5 text-white font-mono"
                required
              />
            </div>

            <button
              type="submit"
              className="w-full py-2 bg-cyan-500 hover:bg-cyan-400 text-black font-bold rounded transition"
            >
              Add Active Sentinel Rule
            </button>
          </form>
        </div>

        {/* Active Rules List */}
        <div className="lg:col-span-2 space-y-4">
          <div className="terminal-card p-5 space-y-3">
            <div className="text-white font-bold text-[11px] flex items-center justify-between">
              <span>ACTIVE SENTINEL RULES ({rules.length})</span>
              <span className="text-[10px] text-emerald-400">● Live Monitoring</span>
            </div>

            <div className="space-y-2 max-h-60 overflow-y-auto">
              {rules.map((r) => (
                <div
                  key={r.rule_id}
                  className="p-3 bg-[#090d16] rounded border border-[#1e293b] flex items-center justify-between gap-3"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-white">{r.symbol}</span>
                      <span className="px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 text-[10px]">
                        {r.rule_type} @ {r.threshold}
                      </span>
                    </div>
                    <div className="text-[#94a3b8] text-[10px] mt-1">{r.message}</div>
                  </div>
                  <button
                    onClick={() => handleDeleteRule(r.rule_id)}
                    className="p-1.5 rounded hover:bg-rose-500/20 text-[#64748b] hover:text-rose-400 transition"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Triggered Alert History */}
          <div className="terminal-card p-5 space-y-3">
            <div className="text-white font-bold text-[11px] flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              <span>RECENT TRIGGERED ALERTS AUDIT LEDGER</span>
            </div>

            <div className="space-y-2 max-h-48 overflow-y-auto">
              {history.map((h, i) => (
                <div
                  key={i}
                  className="p-2.5 bg-[#090d16] rounded border border-[#1e293b] flex items-center justify-between text-[10px]"
                >
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                    <div>
                      <span className="font-bold text-white">{h.symbol}</span>: {h.message}
                    </div>
                  </div>
                  <div className="text-[#64748b]">
                    {new Date(h.timestamp).toLocaleTimeString("en-IN")}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
