"""
Market AI — Bullish Researcher Agent
Scores the bull case from real analyst signals. Higher net signal => higher conviction.
"""

from typing import Dict, Any, List
from agents.llm_provider import LLMClient
from agents.indicators import clamp


class BullishResearcherAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Bullish Researcher"

    async def argue(self, symbol: str, analyst_reports: Dict[str, Any]) -> Dict[str, Any]:
        signals: List[float] = []
        for k in ("fundamentals", "technicals", "sentiment", "macro"):
            s = float(analyst_reports.get(k, {}).get("signal", 0.0))
            signals.append(s)
        net = sum(signals) / max(1, len(signals))

        # Bull conviction only counts positive contribution.
        bull_score = clamp(max(0.0, net) + 0.5 * max(0.0, max(signals) - abs(min(signals))))
        conviction_label = "HIGH" if bull_score > 0.5 else ("MODERATE" if bull_score > 0.2 else "LOW")

        system_prompt = (
            "You are the Lead Bullish Research Analyst. Given the numeric signals, "
            "state the strongest bull case in 3 sentences and cite the drivers."
        )
        user_prompt = (
            f"{symbol}: fundamentals={signals[0]}, technicals={signals[1]}, "
            f"sentiment={signals[2]}, macro={signals[3]}, mean={net:.3f}, bull_score={bull_score:.3f}."
        )
        llm_argument = await self.llm.generate(system_prompt, user_prompt)

        strongest = max(
            ("fundamentals", signals[0]),
            ("technicals", signals[1]),
            ("sentiment", signals[2]),
            ("macro", signals[3]),
            key=lambda x: x[1],
        )
        return {
            "agent": self.name,
            "stance": "BULLISH",
            "conviction": conviction_label,
            "score": round(bull_score, 3),
            "net_signal": round(net, 3),
            "leading_driver": strongest[0],
            "thesis": (
                f"Net analyst signal {net:+.2f} favors upside on {symbol}. "
                f"Leading driver: {strongest[0]} at {strongest[1]:+.2f}."
            ),
            "catalysts": [
                f"{k} contributes {v:+.2f}" for k, v in zip(
                    ("fundamentals", "technicals", "sentiment", "macro"), signals
                ) if v > 0.1
            ] or ["No positive contributors — bull case is weak."],
            "llm_argument": llm_argument,
        }
