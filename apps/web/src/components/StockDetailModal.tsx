"use client";

import React, { useState, useEffect } from "react";
import { X, TrendingUp, TrendingDown, Cpu, Activity, Layers, DollarSign, ShieldAlert, Sparkles } from "lucide-react";
import { MarketAPI } from "@/lib/api";
import { formatINR, formatNumber, formatPercent } from "@/lib/utils";

interface StockDetailModalProps {
  symbol: string | null;
  onClose: () => void;
}

export function StockDetailModal({ symbol, onClose }: StockDetailModalProps) {
  const [details, setDetails] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeSubTab, setActiveSubTab] = useState<string>("overview");
  const [selectedHorizon, setSelectedHorizon] = useState<string>("5D");

  useEffect(() => {
    if (!symbol) return;
    setLoading(true);
    MarketAPI.getStockDetails(symbol)
      .then((data) => {
        setDetails(data);
      })
      .catch((err) => console.error("Error loading stock details:", err))
      .finally(() => setLoading(false));
  }, [symbol]);

  if (!symbol) return null;

  const quote = details?.quote;
  const features = details?.features;
  const prediction = details?.prediction;
  const isUp = (quote?.percent_change || 0) >= 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-[#0c111c] border border-[#1e293b] rounded-xl shadow-glass flex flex-col overflow-hidden animate-in fade-in zoom-in duration-200">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-[#1e293b] flex items-center justify-between bg-[#090d16]">
          <div className="flex items-center gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold font-mono text-white">{symbol}</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                  NSE EQ
                </span>
                <span className="text-xs text-[#64748b] font-mono">
                  {details?.sector || "Indian Equities"}
                </span>
              </div>
              <div className="text-xs text-[#94a3b8]">{details?.name || symbol}</div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {quote && (
              <div className="text-right font-mono">
                <div className="text-xl font-bold text-white">{formatINR(quote.last_price)}</div>
                <div className={`text-xs font-semibold ${isUp ? "text-emerald-400" : "text-rose-400"}`}>
                  {formatPercent(quote.percent_change)} ({isUp ? `+${quote.change}` : quote.change})
                </div>
              </div>
            )}
            <button
              onClick={onClose}
              className="p-2 rounded-lg bg-[#151b2c] hover:bg-[#1e293b] text-[#94a3b8] hover:text-white transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex items-center gap-2 px-6 border-b border-[#1e293b] bg-[#070a10] text-xs font-mono">
          {[
            { id: "overview", label: "Overview & Features", icon: Layers },
            { id: "financials", label: "Financials & Valuation", icon: DollarSign },
            { id: "prediction", label: "AI Directional Forecast", icon: Cpu },
            { id: "corporate", label: "Shareholding & Filings", icon: Activity },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeSubTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveSubTab(tab.id)}
                className={`py-3 px-4 flex items-center gap-2 border-b-2 font-medium transition ${
                  isActive
                    ? "border-cyan-400 text-cyan-400"
                    : "border-transparent text-[#64748b] hover:text-white"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Modal Body Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {loading ? (
            <div className="py-20 text-center font-mono text-xs text-cyan-400 animate-pulse">
              Extracting Quantitative Features and Model Forecasts...
            </div>
          ) : (
            <>
              {/* TAB 1: Overview & Features */}
              {activeSubTab === "overview" && features && (
                <div className="space-y-6">
                  {/* Key Metrics Grid */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono">
                    <div className="bg-[#090d16] p-3 rounded-lg border border-[#1e293b]">
                      <div className="text-[11px] text-[#64748b]">RSI (14)</div>
                      <div className="text-base font-bold text-white mt-1">
                        {features.price_features.rsi_14 ?? "55.0"}
                      </div>
                    </div>
                    <div className="bg-[#090d16] p-3 rounded-lg border border-[#1e293b]">
                      <div className="text-[11px] text-[#64748b]">20-Day SMA</div>
                      <div className="text-base font-bold text-cyan-400 mt-1">
                        {formatINR(features.price_features.sma_20)}
                      </div>
                    </div>
                    <div className="bg-[#090d16] p-3 rounded-lg border border-[#1e293b]">
                      <div className="text-[11px] text-[#64748b]">Alpha vs NIFTY</div>
                      <div className="text-base font-bold text-emerald-400 mt-1">
                        {features.price_features.relative_strength_nifty}
                      </div>
                    </div>
                    <div className="bg-[#090d16] p-3 rounded-lg border border-[#1e293b]">
                      <div className="text-[11px] text-[#64748b]">Volume Z-Score</div>
                      <div className="text-base font-bold text-white mt-1">
                        {features.volume_features.volume_zscore}
                      </div>
                    </div>
                  </div>

                  {/* Technical Breakdown */}
                  <div className="terminal-card p-4">
                    <div className="text-xs font-bold text-white font-mono mb-3">TECHNICAL INDICATORS</div>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs font-mono">
                      <div className="flex justify-between border-b border-[#1e293b] pb-1.5">
                        <span className="text-[#64748b]">50-Day SMA:</span>
                        <span className="text-white">{formatINR(features.price_features.sma_50)}</span>
                      </div>
                      <div className="flex justify-between border-b border-[#1e293b] pb-1.5">
                        <span className="text-[#64748b]">200-Day SMA:</span>
                        <span className="text-white">{formatINR(features.price_features.sma_200)}</span>
                      </div>
                      <div className="flex justify-between border-b border-[#1e293b] pb-1.5">
                        <span className="text-[#64748b]">ATR (14):</span>
                        <span className="text-white">{features.price_features.atr_14}</span>
                      </div>
                      <div className="flex justify-between border-b border-[#1e293b] pb-1.5">
                        <span className="text-[#64748b]">Bollinger Upper:</span>
                        <span className="text-white">{formatINR(features.price_features.bollinger_upper)}</span>
                      </div>
                      <div className="flex justify-between border-b border-[#1e293b] pb-1.5">
                        <span className="text-[#64748b]">Bollinger Lower:</span>
                        <span className="text-white">{formatINR(features.price_features.bollinger_lower)}</span>
                      </div>
                      <div className="flex justify-between border-b border-[#1e293b] pb-1.5">
                        <span className="text-[#64748b]">Delivery %:</span>
                        <span className="text-emerald-400 font-semibold">{features.volume_features.delivery_pct}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 2: Financials & Valuation */}
              {activeSubTab === "financials" && features && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono">
                    <div className="bg-[#090d16] p-4 rounded-lg border border-[#1e293b]">
                      <div className="text-xs text-[#64748b]">P/E Ratio</div>
                      <div className="text-lg font-bold text-white mt-1">
                        {features.fundamental_features.pe_ratio}x
                      </div>
                    </div>
                    <div className="bg-[#090d16] p-4 rounded-lg border border-[#1e293b]">
                      <div className="text-xs text-[#64748b]">P/B Ratio</div>
                      <div className="text-lg font-bold text-white mt-1">
                        {features.fundamental_features.pb_ratio}x
                      </div>
                    </div>
                    <div className="bg-[#090d16] p-4 rounded-lg border border-[#1e293b]">
                      <div className="text-xs text-[#64748b]">Return on Equity</div>
                      <div className="text-lg font-bold text-emerald-400 mt-1">
                        {features.fundamental_features.roe_pct}%
                      </div>
                    </div>
                    <div className="bg-[#090d16] p-4 rounded-lg border border-[#1e293b]">
                      <div className="text-xs text-[#64748b]">Debt to Equity</div>
                      <div className="text-lg font-bold text-white mt-1">
                        {features.fundamental_features.debt_to_equity}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 3: AI Directional Prediction */}
              {activeSubTab === "prediction" && prediction && (
                <div className="space-y-5">
                  <div className="terminal-card p-5 bg-gradient-to-r from-[#0e131f] to-[#151b2c]">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-cyan-400" />
                        <span className="text-sm font-bold text-white font-mono">
                          QUANTITATIVE ML DIRECTIONAL FORECAST
                        </span>
                      </div>
                      <span className="text-xs font-mono text-[#64748b]">
                        Model: {prediction.model_id} ({prediction.model_version})
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-4 font-mono text-center mb-5">
                      <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                        <div className="text-[11px] text-[#64748b]">Forecast Direction</div>
                        <div
                          className={`text-xl font-bold mt-1 ${
                            prediction.direction === "UP" ? "text-emerald-400" : "text-rose-400"
                          }`}
                        >
                          {prediction.direction}
                        </div>
                      </div>
                      <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                        <div className="text-[11px] text-[#64748b]">Win Probability</div>
                        <div className="text-xl font-bold text-white mt-1">
                          {Math.round(prediction.probability * 100)}%
                        </div>
                      </div>
                      <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                        <div className="text-[11px] text-[#64748b]">Expected Return (5D)</div>
                        <div className="text-xl font-bold text-cyan-400 mt-1">
                          {prediction.expected_return > 0 ? `+${prediction.expected_return}%` : `${prediction.expected_return}%`}
                        </div>
                      </div>
                    </div>

                    <div className="space-y-1.5 font-mono text-xs text-[#94a3b8]">
                      <div className="text-[11px] uppercase font-bold text-[#64748b]">Model Explanatory Drivers:</div>
                      {prediction.drivers?.map((d: string, i: number) => (
                        <div key={i} className="flex items-center gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                          <span>{d}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 4: Corporate Filings & Shareholding */}
              {activeSubTab === "corporate" && details?.shareholding_pattern && (
                <div className="space-y-4 font-mono text-xs">
                  <div className="terminal-card p-4">
                    <div className="text-xs font-bold text-white mb-3">SHAREHOLDING PATTERN</div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                        <span className="text-[#64748b]">Promoter:</span>
                        <div className="text-base font-bold text-white mt-1">{details.shareholding_pattern.promoter_pct}%</div>
                      </div>
                      <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                        <span className="text-[#64748b]">FII (Foreign):</span>
                        <div className="text-base font-bold text-cyan-400 mt-1">{details.shareholding_pattern.fii_pct}%</div>
                      </div>
                      <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                        <span className="text-[#64748b]">DII (Domestic):</span>
                        <div className="text-base font-bold text-emerald-400 mt-1">{details.shareholding_pattern.dii_pct}%</div>
                      </div>
                      <div className="bg-[#090d16] p-3 rounded border border-[#1e293b]">
                        <span className="text-[#64748b]">Public / Retail:</span>
                        <div className="text-base font-bold text-white mt-1">{details.shareholding_pattern.public_pct}%</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
