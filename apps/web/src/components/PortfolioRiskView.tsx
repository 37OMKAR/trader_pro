"use client";

import React, { useState, useEffect } from "react";
import { ShieldCheck, AlertOctagon, PieChart, Activity, Zap } from "lucide-react";
import { MarketAPI } from "@/lib/api";
import { formatINR, formatPercent } from "@/lib/utils";

export function PortfolioRiskView() {
  const [riskData, setRiskData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchRisk = async () => {
      try {
        const data = await MarketAPI.getPortfolioRiskAnalysis();
        setRiskData(data);
      } catch (err) {
        console.error("Error fetching risk data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchRisk();
  }, []);

  if (loading) {
    return <div className="terminal-card p-12 text-center text-xs font-mono text-cyan-400">Analyzing Portfolio Value-at-Risk & Stress Models...</div>;
  }

  return (
    <div className="space-y-6 font-mono text-xs">
      {/* Top Header */}
      <div className="terminal-card p-5 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h2 className="text-base font-bold text-white">PORTFOLIO INTELLIGENCE & VALUE-AT-RISK (VaR)</h2>
          </div>
          <div className="text-xs text-[#64748b] mt-0.5">
            Parametric & Historical VaR • Expected Shortfall (CVaR) • Extreme Stress Shock Simulator
          </div>
        </div>
      </div>

      {/* Top Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#090d16] p-4 rounded-lg border border-[#1e293b]">
          <div className="text-[#64748b] text-[10px]">1-DAY 95% VaR (INR)</div>
          <div className="text-xl font-bold text-amber-400 mt-1">₹{riskData?.var_95_inr?.toLocaleString("en-IN")}</div>
          <div className="text-[10px] text-[#64748b] mt-0.5">{riskData?.var_95_pct}% of invested capital</div>
        </div>

        <div className="bg-[#090d16] p-4 rounded-lg border border-[#1e293b]">
          <div className="text-[#64748b] text-[10px]">1-DAY 99% EXTREME VaR</div>
          <div className="text-xl font-bold text-rose-400 mt-1">₹{riskData?.var_99_inr?.toLocaleString("en-IN")}</div>
          <div className="text-[10px] text-[#64748b] mt-0.5">{riskData?.var_99_pct}% tail risk</div>
        </div>

        <div className="bg-[#090d16] p-4 rounded-lg border border-[#1e293b]">
          <div className="text-[#64748b] text-[10px]">EXPECTED SHORTFALL (CVaR 95%)</div>
          <div className="text-xl font-bold text-purple-400 mt-1">₹{riskData?.cvar_95_inr?.toLocaleString("en-IN")}</div>
          <div className="text-[10px] text-[#64748b] mt-0.5">Average loss beyond 95% VaR</div>
        </div>

        <div className="bg-[#090d16] p-4 rounded-lg border border-[#1e293b]">
          <div className="text-[#64748b] text-[10px]">SECTOR CONCENTRATION AUDIT</div>
          <div className="text-sm font-bold text-emerald-400 mt-2">{riskData?.concentration_risk}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sector Allocation Breakdown */}
        <div className="terminal-card p-5 space-y-4">
          <div className="text-white font-bold text-[11px] flex items-center gap-2">
            <PieChart className="w-4 h-4 text-cyan-400" />
            <span>SECTOR ALLOCATION WEIGHTS</span>
          </div>

          <div className="space-y-3">
            {Object.entries(riskData?.sector_allocation || {}).map(([sector, pct]: any) => (
              <div key={sector} className="space-y-1">
                <div className="flex justify-between text-[#94a3b8]">
                  <span>{sector}</span>
                  <span className="font-bold text-white">{pct}%</span>
                </div>
                <div className="w-full bg-[#1e293b] rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-cyan-500 h-1.5 rounded-full"
                    style={{ width: `${Math.min(pct, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Extreme Scenario Stress Tests */}
        <div className="terminal-card p-5 space-y-4">
          <div className="text-white font-bold text-[11px] flex items-center gap-2">
            <Zap className="w-4 h-4 text-amber-400" />
            <span>MACRO STRESS TESTING & SHOCK SCENARIOS</span>
          </div>

          <div className="space-y-2.5">
            {riskData?.stress_tests?.map((st: any, i: number) => (
              <div
                key={i}
                className="p-3 bg-[#090d16] rounded border border-[#1e293b] flex items-center justify-between"
              >
                <div>
                  <div className="font-bold text-white">{st.scenario_name}</div>
                  <div className="text-[#64748b] text-[10px] mt-0.5">Market Shock: {st.market_shock_pct}%</div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-rose-400">₹{st.projected_drawdown_inr?.toLocaleString("en-IN")}</div>
                  <div className="text-[10px] px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-400 inline-block mt-0.5">
                    {st.risk_impact}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
