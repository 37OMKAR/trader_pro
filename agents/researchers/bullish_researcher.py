"""
Market AI — Bullish Researcher Agent
Constructs the strongest bull thesis, identifying upside drivers, growth catalysts, and high-conviction targets.
"""

from typing import Dict, Any, List
from agents.llm_provider import LLMClient


class BullishResearcherAgent:
    """Specialist researcher championing the Bull Case in investment debates."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Bullish Researcher"

    async def argue(self, symbol: str, analyst_reports: Dict[str, Any]) -> Dict[str, Any]:
        fund = analyst_reports.get("fundamentals", {})
        tech = analyst_reports.get("technicals", {})
        macro = analyst_reports.get("macro", {})

        system_prompt = (
            "You are the Lead Bullish Research Analyst at an institutional trading firm. "
            "Your objective is to make the strongest, data-backed case FOR buying/going long on the asset. "
            "Synthesize fundamental strength, technical breakout patterns, and macro tailwinds."
        )

        user_prompt = (
            f"Build the Bull Case for {symbol} based on analyst findings:\n"
            f"- Fundamental Summary: {fund.get('summary')}\n"
            f"- Technical Summary: {tech.get('summary')}\n"
            f"- Macro Environment: {macro.get('summary')}\n\n"
            "Format your argument with: 1. Core Thesis, 2. Three Catalysts for Upside, 3. Upside Target."
        )

        llm_argument = await self.llm.generate(system_prompt, user_prompt)

        return {
            "agent": self.name,
            "stance": "BULLISH",
            "conviction": "HIGH",
            "thesis": (
                f"{symbol} exhibits a rare confluence of double-digit earnings growth, healthy ROE, "
                f"unbroken golden moving average alignment, and supportive institutional inflows. "
                f"The risk-reward profile strongly favors accumulation on dips."
            ),
            "catalysts": [
                "Strong quarterly profit trajectory and market share expansion.",
                "Technical price structure breaking out above multi-week resistance.",
                "Robust macro tailwinds with stable domestic liquidity support.",
            ],
            "llm_argument": llm_argument,
        }
