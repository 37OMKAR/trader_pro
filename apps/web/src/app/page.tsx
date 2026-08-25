"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Sidebar } from "@/components/Sidebar";
import { TopBar } from "@/components/TopBar";
import { IndexSummaryCards } from "@/components/IndexSummaryCards";
import { InteractiveChart } from "@/components/InteractiveChart";
import { MarketBreadthCard } from "@/components/MarketBreadthCard";
import { FiiDiiCard } from "@/components/FiiDiiCard";
import { SectorHeatmap } from "@/components/SectorHeatmap";
import { MarketRegimeBadge } from "@/components/MarketRegimeBadge";
import { TopMoversTable } from "@/components/TopMoversTable";
import { StockDetailModal } from "@/components/StockDetailModal";
import { AIPredictionsView } from "@/components/AIPredictionsView";
import { DerivativesView } from "@/components/DerivativesView";
import { StrategyLabView } from "@/components/StrategyLabView";
import { PaperTradingView } from "@/components/PaperTradingView";
import { TournamentsView } from "@/components/TournamentsView";
import { AgentActivityView } from "@/components/AgentActivityView";
import { AlertsView } from "@/components/AlertsView";
import { PortfolioRiskView } from "@/components/PortfolioRiskView";
import { MarketTutorView } from "@/components/MarketTutorView";
import { MarketAPI } from "@/lib/api";
import {
  MarketStatusResponse,
  IndexQuote,
  Candle,
  MarketBreadth,
  FiiDiiActivity,
  SectorPerformance,
  MarketRegimeState,
  Quote,
} from "@/types";

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [selectedSymbol, setSelectedSymbol] = useState<string>("NIFTY 50");
  const [timeframe, setTimeframe] = useState<string>("1D");
  const [modalStock, setModalStock] = useState<string | null>(null);
  
  // Data States
  const [status, setStatus] = useState<MarketStatusResponse | null>(null);
  const [indices, setIndices] = useState<IndexQuote[]>([]);
  const [candles, setCandles] = useState<Candle[]>([]);
  const [breadth, setBreadth] = useState<MarketBreadth | null>(null);
  const [fiiDii, setFiiDii] = useState<FiiDiiActivity | null>(null);
  const [sectors, setSectors] = useState<SectorPerformance[]>([]);
  const [regime, setRegime] = useState<MarketRegimeState | null>(null);
  const [stocks, setStocks] = useState<Quote[]>([]);
  
  // Loading & Connection States
  const [isLoadingChart, setIsLoadingChart] = useState<boolean>(true);
  const [isConnected, setIsConnected] = useState<boolean>(false);

  // Fetch all initial data
  const loadMarketData = useCallback(async () => {
    try {
      const [
        statusData,
        indicesData,
        breadthData,
        fiiDiiData,
        sectorsData,
        regimeData,
        stocksData,
      ] = await Promise.allSettled([
        MarketAPI.getMarketStatus(),
        MarketAPI.getIndices(),
        MarketAPI.getMarketBreadth(),
        MarketAPI.getFiiDii(),
        MarketAPI.getSectors(),
        MarketAPI.getMarketRegime(),
        MarketAPI.getStocks(20),
      ]);

      if (statusData.status === "fulfilled") setStatus(statusData.value);
      if (indicesData.status === "fulfilled") setIndices(indicesData.value);
      if (breadthData.status === "fulfilled") setBreadth(breadthData.value);
      if (fiiDiiData.status === "fulfilled") setFiiDii(fiiDiiData.value);
      if (sectorsData.status === "fulfilled") setSectors(sectorsData.value);
      if (regimeData.status === "fulfilled") setRegime(regimeData.value);
      if (stocksData.status === "fulfilled") setStocks(stocksData.value);
    } catch (err) {
      console.error("Error loading market data:", err);
    }
  }, []);

  // Fetch Chart Candlestick data on symbol or timeframe change
  const loadChartData = useCallback(async () => {
    setIsLoadingChart(true);
    try {
      const data = await MarketAPI.getIndexHistory(selectedSymbol, timeframe, 60);
      setCandles(data);
    } catch (err) {
      console.error("Error loading chart history:", err);
    } finally {
      setIsLoadingChart(false);
    }
  }, [selectedSymbol, timeframe]);

  useEffect(() => {
    loadMarketData();
  }, [loadMarketData]);

  useEffect(() => {
    loadChartData();
  }, [loadChartData]);

  // WebSocket Live Ticker Subscription
  useEffect(() => {
    let ws: WebSocket | null = null;
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/api/v1/ws/ticker";

    const connectWebSocket = () => {
      try {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.event_type === "TICK") {
              setIndices((prev) =>
                prev.map((item) =>
                  item.symbol === data.symbol
                    ? {
                        ...item,
                        current_value: data.price,
                        change: data.change,
                        percent_change: data.percent_change,
                      }
                    : item
                )
              );

              setStocks((prev) =>
                prev.map((item) =>
                  item.symbol === data.symbol
                    ? {
                        ...item,
                        last_price: data.price,
                        change: data.change,
                        percent_change: data.percent_change,
                      }
                    : item
                )
              );
            }
          } catch (e) {
            // Ignore non-json messages
          }
        };

        ws.onclose = () => {
          setIsConnected(false);
          setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = () => {
          setIsConnected(false);
        };
      } catch (err) {
        setIsConnected(false);
      }
    };

    connectWebSocket();

    return () => {
      if (ws) ws.close();
    };
  }, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#06090e] terminal-grid">
      {/* Institutional Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Terminal Viewport */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        {/* Top Header Bar */}
        <TopBar
          status={status}
          indices={indices}
          isConnected={isConnected}
          onRefresh={() => {
            loadMarketData();
            loadChartData();
          }}
        />

        {/* Scrollable Dashboard Body */}
        <main className="flex-1 overflow-y-auto p-5 space-y-5">
          {/* TAB: F&O Derivatives */}
          {activeTab === "derivatives" && <DerivativesView />}

          {/* TAB: Strategy Lab & Backtest */}
          {activeTab === "strategylab" && <StrategyLabView />}

          {/* TAB: Strategy Tournaments & Leaderboard */}
          {activeTab === "tournaments" && <TournamentsView />}

          {/* TAB: Hermes Supervisor Agent Hub */}
          {activeTab === "agentactivity" && <AgentActivityView />}

          {/* TAB: Paper Trading Terminal */}
          {activeTab === "paper" && <PaperTradingView />}

          {/* TAB: Portfolio Risk & VaR */}
          {activeTab === "risk" && <PortfolioRiskView />}

          {/* TAB: Alert Sentinel Engine */}
          {activeTab === "alerts" && <AlertsView />}

          {/* TAB: AI Market Tutor */}
          {activeTab === "tutor" && <MarketTutorView />}

          {/* TAB: AI Predictions View */}
          {activeTab === "predictions" && (
            <AIPredictionsView
              onSelectStock={(sym) => {
                setModalStock(sym);
              }}
            />
          )}

          {/* TAB: Overview */}
          {activeTab === "overview" && (
            <>
              {/* 1. Benchmark Index Cards */}
              <IndexSummaryCards
                indices={indices}
                selectedSymbol={selectedSymbol}
                onSelectIndex={(sym) => setSelectedSymbol(sym)}
              />

              {/* 2. Primary Chart & Regime Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
                <div className="lg:col-span-2">
                  <InteractiveChart
                    symbol={selectedSymbol}
                    candles={candles}
                    timeframe={timeframe}
                    setTimeframe={setTimeframe}
                    isLoading={isLoadingChart}
                  />
                </div>
                <div className="space-y-5">
                  <MarketRegimeBadge regime={regime} />
                  <MarketBreadthCard breadth={breadth} />
                </div>
              </div>

              {/* 3. Secondary Analytics: FII/DII, Sectors, and Movers */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                <FiiDiiCard fiiDii={fiiDii} />
                <div className="md:col-span-2">
                  <SectorHeatmap sectors={sectors} />
                </div>
              </div>

              {/* 4. Top Equities Movers */}
              <TopMoversTable
                stocks={stocks}
                onSelectStock={(sym) => {
                  setModalStock(sym);
                }}
              />
            </>
          )}
        </main>
      </div>

      {/* Deep-Dive Stock Details Modal */}
      <StockDetailModal symbol={modalStock} onClose={() => setModalStock(null)} />
    </div>
  );
}
