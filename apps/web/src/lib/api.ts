/**
 * Market AI — Web Client API Wrapper
 * Thin fetch wrapper around the FastAPI backend at /api/v1.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    let detail = "";
    try {
      detail = await res.text();
    } catch {}
    throw new Error(`API ${res.status} ${res.statusText}: ${path} ${detail}`);
  }
  return (await res.json()) as T;
}

export const MarketAPI = {
  // Market intelligence
  getMarketStatus: () => request<any>("/market/status"),
  getIndices: () => request<any[]>("/market/indices"),
  getIndexHistory: (symbol: string, timeframe: string, limit = 60) =>
    request<any[]>(`/market/indices/${encodeURIComponent(symbol)}/history?timeframe=${timeframe}&limit=${limit}`),
  getMarketBreadth: () => request<any>("/market/breadth"),
  getFiiDii: () => request<any>("/market/fii-dii"),
  getSectors: () => request<any[]>("/market/sectors"),
  getMarketRegime: () => request<any>("/market/regime"),
  getStocks: (limit = 20) => request<any[]>(`/market/stocks?limit=${limit}`),
  getStockDetails: (symbol: string) => request<any>(`/market/stocks/${encodeURIComponent(symbol)}/details`),
  getStockPrediction: (symbol: string, horizon: string) =>
    request<any>(`/market/predictions/${encodeURIComponent(symbol)}?horizon=${encodeURIComponent(horizon)}`),

  // Derivatives
  getFnoUniverse: () => request<any[]>("/derivatives/fno-universe"),
  getOptionChain: (symbol: string, strikes = 17) =>
    request<any>(`/derivatives/option-chain/${encodeURIComponent(symbol)}?strikes=${strikes}`),

  // Strategy Lab
  getStrategyTemplates: () => request<any[]>("/strategies/templates"),
  generateStrategyFromPrompt: (prompt: string) =>
    request<any>("/strategies/generate-from-prompt", {
      method: "POST",
      body: JSON.stringify({ prompt }),
    }),
  runBacktest: (strategy: any, symbol: string, capital: number) =>
    request<any>("/strategies/backtest", {
      method: "POST",
      body: JSON.stringify({ strategy, symbol, initial_capital: capital }),
    }),

  // Paper trading
  getPaperAccountSummary: () => request<any>("/paper/account/summary"),
  placePaperOrder: (order: any) =>
    request<any>("/paper/orders/place", { method: "POST", body: JSON.stringify(order) }),
  resetPaperAccount: (capital: number) =>
    request<any>("/paper/account/reset", { method: "POST", body: JSON.stringify({ initial_capital: capital }) }),

  // Tournaments
  getTournamentLeaderboard: (asset: string) =>
    request<any>(`/tournaments/leaderboard?asset=${encodeURIComponent(asset)}`),

  // Alerts
  getAlertRules: () => request<any[]>("/alerts/rules"),
  createAlertRule: (rule: any) =>
    request<any>("/alerts/rules", { method: "POST", body: JSON.stringify(rule) }),
  deleteAlertRule: (ruleId: string) =>
    request<any>(`/alerts/rules/${encodeURIComponent(ruleId)}`, { method: "DELETE" }),
  getAlertHistory: () => request<any[]>("/alerts/history"),

  // Research
  getDeepResearch: (symbol: string) => request<any>(`/research/deep-dive/${encodeURIComponent(symbol)}`),

  // Agent activity (Hermes multi-agent deliberations)
  getAgentDeliberations: (symbol: string, research = true) =>
    request<any>(`/agent-hub/deliberations/${encodeURIComponent(symbol)}?research=${research}`),

  // Portfolio risk
  getPortfolioRiskAnalysis: () =>
    request<any>("/risk/portfolio-analysis", { method: "POST", body: JSON.stringify({}) }),

  // Tutor
  askMarketTutor: (question: string) =>
    request<any>("/tutor/ask", { method: "POST", body: JSON.stringify({ question }) }),
};

export default MarketAPI;
