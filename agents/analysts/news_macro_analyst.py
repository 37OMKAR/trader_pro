"""
Market AI — News & Macro Analyst Agent
Derives a macro bias from the benchmark index trend (NIFTY-like) when a real
macro feed isn't attached. If a benchmark candle series is passed via
`benchmark_candles`, we use its own 20d and 60d returns to shape the signal.
Emits a numeric signal for downstream voting.
"""

from typing import Dict, Any, List, Optional
from agents.llm_provider import LLMClient
from agents.indicators import rolling_return_pct, clamp


class NewsMacroAnalystAgent:
    """Benchmark-trend macro proxy."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "News & Macro Analyst"

    async def analyze(
        self,
        symbol: str,
        benchmark_candles: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        benchmark_candles = benchmark_candles or []
        ret20 = rolling_return_pct(benchmark_candles, 20) if benchmark_candles else None
        ret60 = rolling_return_pct(benchmark_candles, 60) if benchmark_candles else None

        # Neutral prior if no benchmark data.
        if ret20 is None and ret60 is None:
            signal = 0.0
            bias = "NEUTRAL"
            confidence = 0.4
            climate = "UNKNOWN_MACRO"
        else:
            r20 = ret20 or 0.0
            r60 = ret60 or 0.0
            signal = clamp(0.6 * clamp(r60 / 12.0) + 0.4 * clamp(r20 / 6.0))
            bias = "FAVORABLE" if signal > 0.15 else ("HOSTILE" if signal < -0.15 else "NEUTRAL")
            confidence = round(clamp(0.4 + abs(signal) * 0.6, 0.4, 1.0), 2)
            climate = "RISK_ON" if signal > 0.15 else ("RISK_OFF" if signal < -0.15 else "STABLE_GROWTH")

        system_prompt = (
            "You are a Senior Macroeconomic Strategist covering India and Emerging Markets. "
            "Given benchmark index trend as the macro proxy, write a concise 2-3 sentence outlook."
        )
        user_prompt = (
            f"Analyze macro for {symbol}. Benchmark 20d return={ret20}%, 60d return={ret60}%. "
            f"Regime: {climate}. Bias: {bias}."
        )
        llm_commentary = await self.llm.generate(system_prompt, user_prompt)

        return {
            "agent": self.name,
            "symbol": symbol,
            "macro_bias": bias,
            "signal": round(signal, 3),
            "confidence": confidence,
            "indicators": {
                "benchmark_return_20d_pct": ret20,
                "benchmark_return_60d_pct": ret60,
                "climate": climate,
            },
            "summary": (
                f"Macro {bias}: benchmark 20d {ret20}%, 60d {ret60}%. "
                f"Signal {round(signal,3)} (conf {confidence})."
            ),
            "llm_commentary": llm_commentary,
        }
