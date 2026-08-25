"use client";

import React, { useState, useEffect } from "react";
import { Briefcase, ArrowUpRight, ArrowDownRight, RefreshCw, Plus, RotateCcw, AlertCircle } from "lucide-react";
import { MarketAPI } from "@/lib/api";
import { formatINR, formatNumber, formatPercent } from "@/lib/utils";

export function PaperTradingView() {
  const [account, setAccount] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [action, setAction] = useState<"BUY" | "SELL">("BUY");
  const [symbol, setSymbol] = useState<string>("RELIANCE");
  const [quantity, setQuantity] = useState<number>(10);
  const [orderType, setOrderType] = useState<string>("MARKET");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [orderMsg, setOrderMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const loadAccount = async () => {
    setLoading(true);
    try {
      const data = await MarketAPI.getPaperAccountSummary();
      setAccount(data);
    } catch (err) {
      console.error("Error loading paper account:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAccount();
  }, []);

  const handlePlaceOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setOrderMsg(null);
    try {
      const res = await MarketAPI.placePaperOrder({
        symbol,
        action,
        quantity: Number(quantity),
        order_type: orderType,
      });
      setOrderMsg({ type: "success", text: res.message || "Order filled successfully!" });
      loadAccount();
    } catch (err: any) {
      setOrderMsg({ type: "error", text: err.message || "Failed to execute order." });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResetAccount = async () => {
    if (!confirm("Reset paper trading portfolio to fresh ₹10,00,000 capital?")) return;
    try {
      await MarketAPI.resetPaperAccount(1_000_000);
      loadAccount();
    } catch (err) {
      console.error("Error resetting account:", err);
    }
  };

  const isProfit = (account?.total_pnl || 0) >= 0;

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="terminal-card p-5 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-cyan-400" />
            <h2 className="text-base font-bold font-mono text-white">
              INSTITUTIONAL PAPER TRADING TERMINAL
            </h2>
          </div>
          <div className="text-xs text-[#64748b] font-mono mt-0.5">
            Simulated ₹10,00,000 Capital Account with Real-Time Mark-to-Market P&L & Indian Fee Modeling
          </div>
        </div>

        <div className="flex items-center gap-3 font-mono text-xs">
          <button
            onClick={handleResetAccount}
            className="px-3 py-1.5 rounded bg-[#151b2c] hover:bg-[#1e293b] text-[#94a3b8] hover:text-white border border-[#1e293b] flex items-center gap-1.5 transition"
            title="Reset Portfolio"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Capital</span>
          </button>

          <button
            onClick={loadAccount}
            className="p-2 rounded bg-[#151b2c] hover:bg-[#1e293b] text-[#94a3b8] hover:text-white border border-[#1e293b] transition"
            title="Refresh Account"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-cyan-400" : ""}`} />
          </button>
        </div>
      </div>

      {/* Portfolio Summary Tiles */}
      {account && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 font-mono">
          <div className="bg-[#090d16] p-4 rounded-lg border border-[#1e293b]">
            <div className="text-[11px] text-[#64748b]">Total Portfolio Value</div>
            <div className="text-xl font-bold text-white mt-1">
              {formatINR(account.total_portfolio_value)}
            </div>
            <div className={`text-xs mt-0.5 font-semibold ${isProfit ? "text-emerald-400" : "text-rose-400"}`}>
              {isProfit ? `+${account.total_pnl_pct}%` : `${account.total_pnl_pct}%`} ({formatINR(account.total_pnl)})
            </div>
          </div>

          <div className="bg-[#090d16] p-4 rounded-lg border border-[#1e293b]">
            <div className="text-[11px] text-[#64748b]">Available Cash Balance</div>
            <div className="text-xl font-bold text-cyan-400 mt-1">
              {formatINR(account.cash_balance)}
            </div>
            <div className="text-xs text-[#64748b] mt-0.5">Ready for deployment</div>
          </div>

          <div className="bg-[#090d16] p-4 rounded-lg border border-[#1e293b]">
            <div className="text-[11px] text-[#64748b]">Holdings Market Value</div>
            <div className="text-xl font-bold text-white mt-1">
              {formatINR(account.current_holdings_value)}
            </div>
            <div className="text-xs text-[#64748b] mt-0.5">
              Unrealized P&L:{" "}
              <span className={account.unrealized_pnl >= 0 ? "text-emerald-400" : "text-rose-400"}>
                {formatINR(account.unrealized_pnl)}
              </span>
            </div>
          </div>

          <div className="bg-[#090d16] p-4 rounded-lg border border-[#1e293b]">
            <div className="text-[11px] text-[#64748b]">Realized P&L (Booked)</div>
            <div className={`text-xl font-bold mt-1 ${account.realized_pnl >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
              {formatINR(account.realized_pnl)}
            </div>
            <div className="text-xs text-[#64748b] mt-0.5">
              Fees Paid: {formatINR(account.total_fees_paid)}
            </div>
          </div>
        </div>
      )}

      {/* Main Grid: Order Entry Form + Open Positions & Trade Log */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Order Placement Form */}
        <div className="terminal-card p-5 font-mono text-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-[#1e293b]">
            <span className="font-bold text-white uppercase">ORDER EXECUTION FORM</span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400">INSTANT FILL</span>
          </div>

          {orderMsg && (
            <div
              className={`p-3 rounded border text-xs flex items-center gap-2 ${
                orderMsg.type === "success"
                  ? "bg-emerald-950/30 border-emerald-500/50 text-emerald-400"
                  : "bg-rose-950/30 border-rose-500/50 text-rose-400"
              }`}
            >
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{orderMsg.text}</span>
            </div>
          )}

          <form onSubmit={handlePlaceOrder} className="space-y-4">
            {/* BUY / SELL Action Switcher */}
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setAction("BUY")}
                className={`py-2 rounded font-bold transition ${
                  action === "BUY"
                    ? "bg-emerald-500 text-black shadow-glow-green"
                    : "bg-[#090d16] text-[#64748b] border border-[#1e293b]"
                }`}
              >
                BUY (LONG)
              </button>
              <button
                type="button"
                onClick={() => setAction("SELL")}
                className={`py-2 rounded font-bold transition ${
                  action === "SELL"
                    ? "bg-rose-500 text-white shadow-glow-red"
                    : "bg-[#090d16] text-[#64748b] border border-[#1e293b]"
                }`}
              >
                SELL (EXIT)
              </button>
            </div>

            {/* Symbol Selector */}
            <div className="space-y-1">
              <label className="text-[#64748b]">Select Stock Asset:</label>
              <select
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                className="w-full bg-[#090d16] border border-[#1e293b] rounded p-2.5 text-white font-mono"
              >
                {["RELIANCE", "TCS", "HDFCBANK", "INFY", "TATAMOTORS", "ICICIBANK", "SBIN", "BHARTIARTL", "BAJFINANCE"].map(
                  (s) => (
                    <option key={s} value={s}>{s}</option>
                  )
                )}
              </select>
            </div>

            {/* Quantity Input */}
            <div className="space-y-1">
              <label className="text-[#64748b]">Quantity (Shares):</label>
              <input
                type="number"
                min={1}
                max={10000}
                value={quantity}
                onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                className="w-full bg-[#090d16] border border-[#1e293b] rounded p-2.5 text-white font-mono"
              />
            </div>

            {/* Order Type */}
            <div className="space-y-1">
              <label className="text-[#64748b]">Order Type:</label>
              <select
                value={orderType}
                onChange={(e) => setOrderType(e.target.value)}
                className="w-full bg-[#090d16] border border-[#1e293b] rounded p-2.5 text-white font-mono"
              >
                <option value="MARKET">MARKET ORDER (Instant Match)</option>
                <option value="LIMIT">LIMIT ORDER</option>
              </select>
            </div>

            <div className="p-3 bg-[#090d16] rounded border border-[#1e293b] space-y-1 text-[11px] text-[#64748b]">
              <div className="flex justify-between">
                <span>Estimated Slippage:</span>
                <span className="text-white">0.05%</span>
              </div>
              <div className="flex justify-between">
                <span>Estimated STT & Brokerage:</span>
                <span className="text-white">0.10% + ₹20 cap</span>
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className={`w-full py-2.5 rounded font-bold transition flex items-center justify-center gap-2 ${
                action === "BUY"
                  ? "bg-emerald-500 hover:bg-emerald-400 text-black"
                  : "bg-rose-500 hover:bg-rose-400 text-white"
              } disabled:opacity-50`}
            >
              <Plus className="w-4 h-4" />
              <span>{isSubmitting ? "Executing Trade..." : `Submit ${action} Order`}</span>
            </button>
          </form>
        </div>

        {/* Positions & Trade History Tabs */}
        <div className="lg:col-span-2 space-y-4 font-mono text-xs">
          {/* Active Holdings Table */}
          <div className="terminal-card p-5">
            <div className="flex items-center justify-between pb-3 border-b border-[#1e293b] mb-4">
              <span className="font-bold text-white uppercase">
                ACTIVE OPEN POSITIONS ({account?.positions?.length || 0})
              </span>
              <span className="text-[11px] text-[#64748b]">Live MTM Valuation</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-[#1e293b] text-[11px] text-[#64748b]">
                    <th className="pb-2">ASSET</th>
                    <th className="pb-2 text-right">QTY</th>
                    <th className="pb-2 text-right">AVG (₹)</th>
                    <th className="pb-2 text-right">LTP (₹)</th>
                    <th className="pb-2 text-right">VALUE (₹)</th>
                    <th className="pb-2 text-right">UNREALIZED P&L</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1e293b]/50">
                  {account?.positions?.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-8 text-center text-[#64748b]">
                        No active open positions. Place an order to build your virtual portfolio.
                      </td>
                    </tr>
                  ) : (
                    account?.positions?.map((pos: any) => {
                      const isPosProfit = pos.unrealized_pnl >= 0;
                      return (
                        <tr key={pos.symbol} className="hover:bg-[#0e131f] transition">
                          <td className="py-2.5 font-bold text-white">{pos.symbol}</td>
                          <td className="py-2.5 text-right text-white">{pos.quantity}</td>
                          <td className="py-2.5 text-right text-[#94a3b8]">₹{pos.average_price}</td>
                          <td className="py-2.5 text-right font-semibold text-white">₹{pos.current_price}</td>
                          <td className="py-2.5 text-right text-white">{formatINR(pos.current_value)}</td>
                          <td className={`py-2.5 text-right font-bold ${isPosProfit ? "text-emerald-400" : "text-rose-400"}`}>
                            {isPosProfit ? "+" : ""}{formatINR(pos.unrealized_pnl)} ({isPosProfit ? "+" : ""}{pos.unrealized_pnl_pct}%)
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Trade Execution History */}
          <div className="terminal-card p-5">
            <div className="flex items-center justify-between pb-3 border-b border-[#1e293b] mb-3">
              <span className="font-bold text-white uppercase">ORDER HISTORY & FILLS LOG</span>
              <span className="text-[11px] text-[#64748b]">Audited Transactions</span>
            </div>

            <div className="max-h-52 overflow-y-auto space-y-1.5">
              {account?.trade_history?.length === 0 ? (
                <div className="text-center py-6 text-[#64748b]">No executed orders yet.</div>
              ) : (
                account?.trade_history?.map((trade: any, idx: number) => {
                  const isBuy = trade.action === "BUY";
                  return (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-2.5 bg-[#090d16] rounded border border-[#1e293b]/70"
                    >
                      <div className="flex items-center gap-3">
                        <span
                          className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                            isBuy ? "bg-emerald-500/15 text-emerald-400" : "bg-rose-500/15 text-rose-400"
                          }`}
                        >
                          {trade.action}
                        </span>
                        <div>
                          <span className="font-bold text-white">{trade.symbol}</span>
                          <span className="text-[#64748b] ml-2">
                            {trade.quantity} shares @ ₹{trade.price}
                          </span>
                        </div>
                      </div>

                      <div className="text-right text-[11px]">
                        <div className="text-[#94a3b8]">Fee: ₹{trade.fee}</div>
                        {trade.pnl !== undefined && (
                          <div className={`font-bold ${trade.pnl >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                            P&L: {trade.pnl >= 0 ? "+" : ""}{formatINR(trade.pnl)}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
