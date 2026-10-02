/**
 * Market AI — Typed REST client for the FastAPI backend.
 * All endpoints are routed under `/api/v1` (see apps/api/app/core/config.py).
 */

import type {
  MarketStatusResponse,
  IndexQuote,
  Candle,
  MarketBreadth,
  FiiDiiActivity,
  SectorPerformance,
  MarketRegimeState,
  Quote,
} from "@/types";

const BASE_URL =
  (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL) ||
  "http://127.0.0.1:8000";
const API = `${BASE_URL}/api/v1`;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    cache: "no-store",
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    ...init,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} — ${path} — ${body.slice(0, 200)}`);
  }
  if (res.status === 204) return undefined as unknown as T;
  return (await res.json()) as T;
}

const GET  = <T,>(path: string) => request<T>(path);
const POST = <T,>(path: string, body?: unknown) =>
  request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined });
const DEL  = <T,>(path: string) => request<T>(path, { method: "DELETE" });

export const MarketAPI = {
  // ─── Market Intelligence ─────────────────────────────────────────────
  getMarketStatus:   ()                                                      => GET<MarketStatusResponse>("/market/status"),
  getIndices:        ()                                                      => GET<IndexQuote[]>("/market/indices"),
  getIndexHistory:   (symbol: string, timeframe = "1D", limit = 60)          =>
    GET<Candle[]>(`/market/indices/${encodeURIComponent(symbol)}/history?timeframe=${timeframe}&limit=${limit}`),
  getMarketBreadth:  ()                                                      => GET<MarketBreadth>("/market/breadth"),
  getFiiDii:         ()                                                      => GET<FiiDiiActivity>("/market/fii-dii"),
  getSectors:        ()                                                      => GET<SectorPerformance[]>("/market/sectors"),
  getMarketRegime:   ()                                                      => GET<MarketRegimeState>("/market/regime"),
  getStocks:         (limit = 20)                                            => GET<Quote[]>(`/market/stocks?limit=${limit}`),
  getStockDetails:   (symbol: string)                                        => GET<Record<string, unknown>>(`/market/stocks/${encodeURIComponent(symbol)}/details`),
  getStockPrediction:(symbol: string, horizon?: string)                      =>
    GET<Record<string, unknown>>(`/market/predictions/${encodeURIComponent(symbol)}${horizon ? `?horizon=${horizon}` : ""}`),

  // ─── Derivatives ─────────────────────────────────────────────────────
  getFnoUniverse:    ()                                                      => GET<Record<string, unknown>[]>("/derivatives/fno-universe"),
  getOptionChain:    (symbol: string, strikes = 17)                          =>
    GET<Record<string, unknown>>(`/derivatives/option-chain/${encodeURIComponent(symbol)}?strikes=${strikes}`),

  // ─── Strategy Lab ────────────────────────────────────────────────────
  getStrategyTemplates:        ()                                            => GET<Record<string, unknown>[]>("/strategies/templates"),
  generateStrategyFromPrompt:  (prompt: string)                              => POST<Record<string, unknown>>("/strategies/generate-from-prompt", { prompt }),
  runBacktest:                 (strategy: unknown, symbol: string, capital = 1_000_000) =>
    POST<Record<string, unknown>>("/strategies/backtest", { strategy, symbol, capital }),

  // ─── Paper Trading ───────────────────────────────────────────────────
  getPaperAccountSummary: ()                                                 => GET<Record<string, unknown>>("/paper/account/summary"),
  placePaperOrder:        (payload: {
    symbol: string; action: string; quantity: number;
    order_type?: string; limit_price?: number;
    stop_loss?: number | null; target?: number | null;
  })                                                                         => POST<Record<string, unknown>>("/paper/orders/place", payload),
  resetPaperAccount:      (initial_balance = 1_000_000)                      => POST<Record<string, unknown>>("/paper/account/reset", { initial_balance }),

  // ─── Tournaments & Evolution ─────────────────────────────────────────
  getTournamentLeaderboard: (asset?: string) =>
    GET<Record<string, unknown>>(`/tournaments/leaderboard${asset ? `?asset=${encodeURIComponent(asset)}` : ""}`),

  // ─── Hermes Agent Hub ────────────────────────────────────────────────
  getAgentDeliberations: (symbol: string)                                    => GET<Record<string, unknown>>(`/agent-hub/deliberations/${encodeURIComponent(symbol)}`),

  // ─── Research ────────────────────────────────────────────────────────
  getDeepResearch:   (symbol: string)                                        => GET<Record<string, unknown>>(`/research/deep-dive/${encodeURIComponent(symbol)}`),

  // ─── Alerts ──────────────────────────────────────────────────────────
  getAlertRules:     ()                                                      => GET<Record<string, unknown>[]>("/alerts/rules"),
  getAlertHistory:   ()                                                      => GET<Record<string, unknown>[]>("/alerts/history"),
  createAlertRule:   (rule: Record<string, unknown>)                         => POST<Record<string, unknown>>("/alerts/rules", rule),
  deleteAlertRule:   (ruleId: string)                                        => DEL<Record<string, unknown>>(`/alerts/rules/${encodeURIComponent(ruleId)}`),

  // ─── Portfolio Risk ──────────────────────────────────────────────────
  getPortfolioRiskAnalysis: ()                                               => POST<Record<string, unknown>>("/risk/portfolio-analysis", {}),

  // ─── Market Tutor ────────────────────────────────────────────────────
  askMarketTutor:    (question: string)                                      => POST<Record<string, unknown>>("/tutor/ask", { question }),

  // ─── Voice & Avatar ──────────────────────────────────────────────────
  synthesizeBriefing: (text: string)                                         => POST<Record<string, unknown>>("/voice/synthesize-briefing", { text }),
  generateAvatar:     (text: string)                                         => POST<Record<string, unknown>>("/voice/generate-avatar", { text }),

  // ─── Skills Registry ─────────────────────────────────────────────────
  listSkills:        ()                                                      => GET<Record<string, unknown>[]>("/skills"),
  getSkill:          (id: string)                                            => GET<Record<string, unknown>>(`/skills/${encodeURIComponent(id)}`),
};

export type { MarketStatusResponse, IndexQuote, Candle, MarketBreadth,
              FiiDiiActivity, SectorPerformance, MarketRegimeState, Quote };
