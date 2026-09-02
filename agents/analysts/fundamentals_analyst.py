"""
Market AI — Fundamentals Analyst Agent
Derives price-based fundamental proxies (52w positioning, volatility, drawdown)
that vary per symbol from real candle data. Emits a numeric signal for voting.

NOTE: A production build should replace the price proxies here with real
statement data (P/E, ROE, debt/equity) from a fundamentals provider.
Until then we compute honest, symbol-varying features from what we have.
"""

from typing import Dict, Any, List
from agents.llm_provider import LLMClient
from agents.indicators import (
    annualized_volatility, rolling_return_pct, drawdown_from_peak_pct, clamp
)


class FundamentalsAnalystAgent:
    """Price-proxy fundamentals scorer."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Fundamentals Analyst"

    async def analyze(
        self,
        symbol: str,
        quote_data: Dict[str, Any],
        candles: List[Any] = None,
    ) -> Dict[str, Any]:
        candles = candles or []
        last_price = float(quote_data.get("last_price", 0.0)) or (float(candles[-1].close) if candles else 1000.0)
        hi52 = float(quote_data.get("high_52w") or (max((c.high for c in candles), default=last_price)))
        lo52 = float(quote_data.get("low_52w") or (min((c.low for c in candles), default=last_price)))

        # Positioning within the 52-week range: 0 = at low, 1 = at high
        rng = max(1e-6, hi52 - lo52)
        pos_52w = clamp((last_price - lo52) / rng, 0.0, 1.0)

        # Realized annualized volatility (a proxy for risk quality)
        vol = annualized_volatility(candles, period=20) or 25.0

        # Trailing return (60d) as a growth proxy
        ret60 = rolling_return_pct(candles, 60) or 0.0
        dd = drawdown_from_peak_pct(candles, 60) or 0.0

        # Composite quality score in [-1, +1]:
        # + positive on strong 60d return
        # + neutral in mid 52w range, penalty at extremes (too hot / too weak)
        # - penalty on high volatility, deep drawdown
        growth_sig = clamp(ret60 / 15.0)
        range_sig = 1.0 - abs(pos_52w - 0.6) * 2.0   # peaks at 60% of range
        vol_penalty = clamp(-max(0.0, (vol - 25.0) / 25.0))
        dd_penalty = clamp(dd / 15.0)  # dd is negative, so this is negative

        signal = clamp(0.5 * growth_sig + 0.2 * range_sig + 0.15 * vol_penalty + 0.15 * dd_penalty)
        rating = "BULLISH" if signal > 0.2 else ("BEARISH" if signal < -0.2 else "NEUTRAL")
        confidence = round(clamp(0.4 + abs(signal) * 0.6, 0.4, 1.0), 2)

        system_prompt = (
            "You are an Indian Equity Fundamental Analyst. Given the price-quality proxies below, "
            "write a concise 2-3 sentence verdict on the risk-adjusted attractiveness."
        )
        user_prompt = (
            f"{symbol}: LTP ₹{last_price}, 52w range ₹{lo52}-₹{hi52} (positioning {pos_52w:.2f}), "
            f"60d return {ret60}%, drawdown from peak {dd}%, annualized volatility {vol}%. "
            f"Rating: {rating}."
        )
        llm_commentary = await self.llm.generate(system_prompt, user_prompt)

        return {
            "agent": self.name,
            "symbol": symbol,
            "rating": rating,
            "signal": round(signal, 3),
            "confidence": confidence,
            "metrics": {
                "position_in_52w_range": round(pos_52w, 3),
                "annualized_volatility_pct": vol,
                "return_60d_pct": ret60,
                "drawdown_from_peak_pct": dd,
                "high_52w": hi52,
                "low_52w": lo52,
            },
            "summary": (
                f"52w positioning {pos_52w:.2f}, 60d return {ret60}%, drawdown {dd}%, vol {vol}%. "
                f"Rating {rating} (signal {round(signal,3)}, conf {confidence})."
            ),
            "llm_commentary": llm_commentary,
        }
