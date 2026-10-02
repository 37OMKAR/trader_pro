"""
Market AI — Fundamentals Analyst Agent
Evaluates valuation ratios, profitability, debt levels, and quarterly growth.

Fundamentals data is sector-aware and per-symbol deterministic. When a real
financial-statements provider is wired, swap `_estimate_fundamentals` for the
provider call — the output contract (metrics dict + rating) stays the same.
"""

import hashlib
from typing import Dict, Any, Optional
from agents.llm_provider import LLMClient


SECTOR_PROFILES: Dict[str, Dict[str, float]] = {
    "IT":              {"pe": 28.0, "pb": 7.5, "roe": 25.0, "roce": 32.0, "de": 0.05, "rev_g": 11.0, "pro_g": 13.0},
    "Banking":         {"pe": 16.5, "pb": 2.2, "roe": 16.0, "roce": 17.5, "de": 1.20, "rev_g": 14.0, "pro_g": 18.0},
    "Financials":      {"pe": 22.0, "pb": 3.4, "roe": 18.0, "roce": 19.5, "de": 2.80, "rev_g": 16.0, "pro_g": 20.0},
    "Energy":          {"pe": 14.0, "pb": 1.9, "roe": 12.0, "roce": 14.0, "de": 0.55, "rev_g": 8.0,  "pro_g": 9.0},
    "FMCG":            {"pe": 55.0, "pb": 11.0, "roe": 22.0, "roce": 28.0, "de": 0.15, "rev_g": 10.0, "pro_g": 12.0},
    "Pharma":          {"pe": 30.0, "pb": 4.5, "roe": 18.0, "roce": 20.0, "de": 0.25, "rev_g": 12.0, "pro_g": 15.0},
    "Automobile":      {"pe": 24.0, "pb": 4.0, "roe": 15.0, "roce": 17.0, "de": 0.60, "rev_g": 13.0, "pro_g": 16.0},
    "Metals & Mining": {"pe": 11.0, "pb": 1.6, "roe": 11.0, "roce": 13.0, "de": 0.70, "rev_g": 7.0,  "pro_g": 6.0},
    "Infrastructure":  {"pe": 20.0, "pb": 3.0, "roe": 14.0, "roce": 15.0, "de": 0.90, "rev_g": 11.0, "pro_g": 12.0},
    "Telecom":         {"pe": 60.0, "pb": 5.5, "roe": 10.0, "roce": 12.0, "de": 1.80, "rev_g": 13.0, "pro_g": 14.0},
    "Consumer":        {"pe": 65.0, "pb": 20.0, "roe": 28.0, "roce": 34.0, "de": 0.10, "rev_g": 12.0, "pro_g": 14.0},
}
_DEFAULT_PROFILE = {"pe": 22.0, "pb": 3.5, "roe": 15.0, "roce": 17.0, "de": 0.60, "rev_g": 10.0, "pro_g": 11.0}


def _jitter(symbol: str, key: str, base: float, spread: float) -> float:
    """Deterministic per-symbol variation around a sector base."""
    seed = int(hashlib.md5(f"{symbol}:{key}".encode()).hexdigest()[:8], 16)
    normalized = (seed % 1000) / 999.0  # [0, 1]
    delta = (normalized - 0.5) * 2.0 * spread
    return round(base + delta, 2)


def _estimate_fundamentals(symbol: str, sector: Optional[str]) -> Dict[str, float]:
    profile = SECTOR_PROFILES.get(sector or "", _DEFAULT_PROFILE)
    return {
        "pe_ratio":           _jitter(symbol, "pe", profile["pe"], profile["pe"] * 0.15),
        "pb_ratio":           _jitter(symbol, "pb", profile["pb"], profile["pb"] * 0.20),
        "roe_pct":            _jitter(symbol, "roe", profile["roe"], 3.0),
        "roce_pct":           _jitter(symbol, "roce", profile["roce"], 3.0),
        "debt_to_equity":     max(0.0, _jitter(symbol, "de", profile["de"], profile["de"] * 0.30)),
        "revenue_growth_pct": _jitter(symbol, "rev_g", profile["rev_g"], 4.0),
        "profit_growth_pct":  _jitter(symbol, "pro_g", profile["pro_g"], 5.0),
    }


class FundamentalsAnalystAgent:
    """Specialized agent analyzing company financial health and valuation."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Fundamentals Analyst"

    async def analyze(self, symbol: str, quote_data: Dict[str, Any]) -> Dict[str, Any]:
        last_price = float(quote_data.get("last_price", 0.0))
        sector = quote_data.get("sector")
        metrics = _estimate_fundamentals(symbol, sector)

        pe = metrics["pe_ratio"]
        pb = metrics["pb_ratio"]
        roe = metrics["roe_pct"]
        de = metrics["debt_to_equity"]
        pro_g = metrics["profit_growth_pct"]

        strong = roe > 15 and de < 1.0 and pro_g > 12
        weak = roe < 8 or de > 2.0 or pro_g < 0
        if strong:
            rating = "STRONG_BUY"
        elif weak:
            rating = "SELL"
        else:
            rating = "NEUTRAL"

        system_prompt = (
            "You are a Senior Indian Equity Fundamental Analyst. "
            "Evaluate financial ratios (P/E, P/B, ROE, Debt/Equity, Earnings growth). "
            "Keep your output clear, concise, and professional."
        )
        user_prompt = (
            f"Analyze fundamentals for {symbol} (sector: {sector or 'Diversified'}):\n"
            f"- Price: ₹{last_price}\n"
            f"- P/E: {pe}x, P/B: {pb}x\n"
            f"- ROE: {roe}%, ROCE: {metrics['roce_pct']}%\n"
            f"- Debt/Equity: {de}\n"
            f"- Revenue Growth (YoY): {metrics['revenue_growth_pct']}%\n"
            f"- Net Profit Growth (YoY): {pro_g}%\n\n"
            "Provide: 1. Valuation Assessment, 2. Balance Sheet Strength, 3. Fundamental Rating (Bullish/Neutral/Bearish)."
        )
        llm_commentary = await self.llm.generate(system_prompt, user_prompt)

        return {
            "agent": self.name,
            "symbol": symbol,
            "rating": rating,
            "metrics": metrics,
            "data_source": "sector_profile_estimated",
            "summary": (
                f"{symbol} ({sector or 'Diversified'}): ROE {roe}% on D/E {de} with YoY profit growth of {pro_g}%. "
                f"Trading at P/E {pe}x, P/B {pb}x. Rating: {rating}."
            ),
            "llm_commentary": llm_commentary,
        }
