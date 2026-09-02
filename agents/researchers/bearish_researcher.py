"""
Market AI — Bearish Researcher Agent
Scores the bear case from real analyst signals. Lower (more negative) net signal => higher conviction.
"""

from typing import Dict, Any, List
from agents.llm_provider import LLMClient
from agents.indicators import clamp


class BearishResearcherAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Bearish Researcher"

    async def argue(self, symbol: str, analyst_reports: Dict[str, Any]) -> Dict[str, Any]:
        signals: List[float] = []
        for k in ("fundamentals", "technicals", "sentiment", "macro"):
            s = float(analyst_reports.get(k, {}).get("signal", 0.0))
            signals.append(s)
        net = sum(signals) / max(1, len(signals))

        bear_score = clamp(max(0.0, -net) + 0.5 * max(0.0, abs(min(signals)) - max(signals)))
        conviction_label = "HIGH" if bear_score > 0.5 else ("MODERATE" if bear_score > 0.2 else "LOW")

        system_prompt = (
            "You are the Chief Skeptic. Given the numeric signals, "
            "state the strongest bear case in 3 sentences and cite the vulnerabilities."
        )
        user_prompt = (
            f"{symbol}: fundamentals={signals[0]}, technicals={signals[1]}, "
            f"sentiment={signals[2]}, macro={signals[3]}, mean={net:.3f}, bear_score={bear_score:.3f}."
        )
        llm_argument = await self.llm.generate(system_prompt, user_prompt)

        weakest = min(
            ("fundamentals", signals[0]),
            ("technicals", signals[1]),
            ("sentiment", signals[2]),
            ("macro", signals[3]),
            key=lambda x: x[1],
        )
        return {
            "agent": self.name,
            "stance": "BEARISH",
            "conviction": conviction_label,
            "score": round(bear_score, 3),
            "net_signal": round(net, 3),
            "leading_risk": weakest[0],
            "thesis": (
                f"Net analyst signal {net:+.2f} for {symbol}. "
                f"Weakest pillar: {weakest[0]} at {weakest[1]:+.2f}."
            ),
            "risk_triggers": [
                f"{k} drags at {v:+.2f}" for k, v in zip(
                    ("fundamentals", "technicals", "sentiment", "macro"), signals
                ) if v < -0.1
            ] or ["No clear negative contributors — bear case is weak."],
            "llm_argument": llm_argument,
        }
