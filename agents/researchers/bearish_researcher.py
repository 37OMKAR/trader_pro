"""
Market AI — Bearish Researcher Agent
Constructs the strongest bear thesis, stress-testing valuation, risks, execution failure points, and downside targets.
"""

from typing import Dict, Any, List
from agents.llm_provider import LLMClient


class BearishResearcherAgent:
    """Specialist researcher championing the Bear Case and downside risk scrutiny."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Bearish Researcher"

    async def argue(self, symbol: str, analyst_reports: Dict[str, Any]) -> Dict[str, Any]:
        fund = analyst_reports.get("fundamentals", {})
        tech = analyst_reports.get("technicals", {})
        macro = analyst_reports.get("macro", {})

        system_prompt = (
            "You are the Chief Skeptic & Bearish Research Analyst at an institutional trading firm. "
            "Your objective is to stress-test the investment hypothesis, find flaws, downside vulnerabilities, "
            "margin compression risks, and reason why this trade might fail."
        )

        user_prompt = (
            f"Build the Bear Case / Risk Thesis for {symbol}:\n"
            f"- Fundamental Summary: {fund.get('summary')}\n"
            f"- Technical Summary: {tech.get('summary')}\n"
            f"- Macro Environment: {macro.get('summary')}\n\n"
            "Format your argument with: 1. Key Vulnerabilities, 2. Three Risk Triggers, 3. Downside Support Breakdown Level."
        )

        llm_argument = await self.llm.generate(system_prompt, user_prompt)

        return {
            "agent": self.name,
            "stance": "BEARISH",
            "conviction": "MODERATE",
            "thesis": (
                f"While top-line growth is sound, {symbol} faces near-term multiple compression if broader "
                f"market momentum slows. Immediate overhead resistance poses a false breakout trap if volume falters."
            ),
            "risk_triggers": [
                "Overhead technical resistance cluster creating supply overhang.",
                "Potential raw material input inflation dampening operating margins.",
                "Global yield spikes that could trigger sudden foreign institutional profit-taking.",
            ],
            "llm_argument": llm_argument,
        }
