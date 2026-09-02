"""
Market AI — Technical Analyst Agent
Computes real SMAs, RSI, ATR, momentum and support/resistance from the candle series.
Emits a numeric signal in [-1, +1] plus confidence for downstream voting.
"""

from typing import Dict, Any, List
from agents.llm_provider import LLMClient
from agents.indicators import (
    sma, rsi, atr, rolling_return_pct, support_resistance, volume_zscore, clamp
)


class TechnicalAnalystAgent:
    """Agent that reads candles, computes indicators, and casts a directional vote."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Technical Analyst"

    async def analyze(self, symbol: str, quote_data: Dict[str, Any], candles: List[Any]) -> Dict[str, Any]:
        last_price = float(quote_data.get("last_price", 0.0)) or (float(candles[-1].close) if candles else 1000.0)

        s20 = sma(candles, 20) or last_price
        s50 = sma(candles, 50) or last_price
        s200 = sma(candles, 200) or last_price * 0.92
        r14 = rsi(candles, 14) or 50.0
        a14 = atr(candles, 14) or (last_price * 0.02)
        ret5 = rolling_return_pct(candles, 5) or 0.0
        ret20 = rolling_return_pct(candles, 20) or 0.0
        vzs = volume_zscore(candles, 20) or 0.0
        support_1, resistance_1 = support_resistance(candles, 20)
        support_2, resistance_2 = support_resistance(candles, 60)
        support_1 = support_1 or round(last_price * 0.97, 2)
        support_2 = support_2 or round(last_price * 0.94, 2)
        resistance_1 = resistance_1 or round(last_price * 1.03, 2)
        resistance_2 = resistance_2 or round(last_price * 1.06, 2)

        # Trend classification from real alignment
        if last_price > s20 > s50 > s200:
            trend = "BULLISH"
        elif last_price < s20 < s50 < s200:
            trend = "BEARISH"
        else:
            trend = "NEUTRAL"

        # Signal composition (each component in [-1, +1])
        trend_sig = clamp(((last_price / s50) - 1.0) * 10.0) if s50 > 0 else 0.0
        # RSI: 30 → -1, 70 → +1, 50 → 0
        rsi_sig = clamp((r14 - 50.0) / 20.0)
        # Momentum
        mom_sig = clamp(ret20 / 10.0)
        # Volume confirmation is a multiplier, not a direction
        vol_conf = clamp(1.0 + max(-0.5, min(0.5, vzs / 4.0)), 0.5, 1.5)

        signal = clamp((0.5 * trend_sig + 0.3 * mom_sig + 0.2 * rsi_sig) * (vol_conf / 1.0))
        # Confidence: stronger when trend, RSI, and momentum agree on sign
        agree = sum(1 for x in (trend_sig, rsi_sig, mom_sig) if (x > 0) == (signal > 0) and abs(x) > 0.1)
        confidence = round(0.4 + 0.2 * agree, 2)  # 0.4..1.0

        system_prompt = (
            "You are an Institutional Technical Analyst focusing on NSE Indian Equities. "
            "Given real indicator values, briefly justify your directional call in 2-3 sentences."
        )
        user_prompt = (
            f"{symbol}: LTP ₹{last_price}, 20DMA ₹{s20}, 50DMA ₹{s50}, 200DMA ₹{s200}. "
            f"RSI(14)={r14}, ATR(14)=₹{a14}, 20-day return={ret20}%, volume z-score={vzs}. "
            f"Support ₹{support_1}/₹{support_2}, Resistance ₹{resistance_1}/₹{resistance_2}. "
            f"Trend={trend}. Provide concise assessment."
        )
        llm_commentary = await self.llm.generate(system_prompt, user_prompt)

        return {
            "agent": self.name,
            "symbol": symbol,
            "trend": trend,
            "signal": round(signal, 3),
            "confidence": confidence,
            "indicators": {
                "sma_20": s20, "sma_50": s50, "sma_200": s200,
                "rsi_14": r14, "atr_14": a14,
                "return_5d_pct": ret5, "return_20d_pct": ret20,
                "volume_zscore": vzs,
                "support_1": support_1, "support_2": support_2,
                "resistance_1": resistance_1, "resistance_2": resistance_2,
            },
            "summary": (
                f"{trend} setup: LTP ₹{last_price} vs 50DMA ₹{s50}, RSI {r14}, "
                f"20d return {ret20}%, ATR ₹{a14}. Signal {round(signal,3)} (conf {confidence})."
            ),
            "llm_commentary": llm_commentary,
        }
