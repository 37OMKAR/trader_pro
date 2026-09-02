"""
Market AI — Sentiment Analyst Agent
Derives a sentiment proxy from price/volume behavior when a real
sentiment feed isn't wired: rising volume on up days = bullish tape,
falling volume on up days = distribution, and the reverse for down days.
Emits a numeric signal for downstream voting.
"""

from typing import Dict, Any, List
from agents.llm_provider import LLMClient
from agents.indicators import volume_zscore, rolling_return_pct, clamp


class SentimentAnalystAgent:
    """Tape-based sentiment proxy in the absence of a live social feed."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Sentiment Analyst"

    async def analyze(
        self,
        symbol: str,
        quote_data: Dict[str, Any] = None,
        candles: List[Any] = None,
    ) -> Dict[str, Any]:
        candles = candles or []
        vzs = volume_zscore(candles, 20) or 0.0
        ret5 = rolling_return_pct(candles, 5) or 0.0

        # Up-days on above-average volume = bullish participation.
        # Down-days on above-average volume = distribution.
        participation = vzs if ret5 >= 0 else -vzs
        signal = clamp(0.6 * clamp(ret5 / 8.0) + 0.4 * clamp(participation / 3.0))
        classification = "BULLISH" if signal > 0.2 else ("BEARISH" if signal < -0.2 else "NEUTRAL")
        sentiment_score = int(round(50 + signal * 50))
        confidence = round(clamp(0.4 + abs(signal) * 0.5, 0.4, 1.0), 2)

        system_prompt = (
            "You are a Quant Sentiment & Derivatives Analyst. Given tape-based cues, "
            "provide a concise 2-3 sentence verdict on flow and positioning."
        )
        user_prompt = (
            f"{symbol}: 5-day return {ret5}%, volume z-score {vzs}, participation {participation:.2f}. "
            f"Sentiment: {classification}."
        )
        llm_commentary = await self.llm.generate(system_prompt, user_prompt)

        return {
            "agent": self.name,
            "symbol": symbol,
            "signal": round(signal, 3),
            "confidence": confidence,
            "sentiment_score": sentiment_score,
            "sentiment_classification": classification,
            "volume_zscore": vzs,
            "return_5d_pct": ret5,
            "summary": (
                f"Tape sentiment {classification} (score {sentiment_score}/100). "
                f"5d return {ret5}% on volume z {vzs}. Signal {round(signal,3)} (conf {confidence})."
            ),
            "llm_commentary": llm_commentary,
        }
