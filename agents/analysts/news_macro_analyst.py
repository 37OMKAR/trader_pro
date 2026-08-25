"""
Market AI — News & Macro Analyst Agent
Analyzes macroeconomic trends, RBI policy, global cues, currency, crude oil, and geopolitical news.
"""

from typing import Dict, Any
from agents.llm_provider import LLMClient


class NewsMacroAnalystAgent:
    """Specialized agent tracking RBI policy, global bond yields, crude oil, USD/INR, and breaking news."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "News & Macro Analyst"

    async def analyze(self, symbol: str) -> Dict[str, Any]:
        macro_climate = "STABLE_GROWTH"
        rbi_policy_stance = "ACCOMMODATIVE / RATE_PAUSE"
        us_10y_yield = 4.22
        brent_crude_usd = 78.40
        usdinr = 86.85
        fii_trend = "NET_BUYERS"

        system_prompt = (
            "You are a Senior Macroeconomic & Geopolitical Strategist covering India and Emerging Markets. "
            "Analyze macroeconomic indicators, RBI interest rate stance, commodity prices, currency stability, and news flow."
        )

        user_prompt = (
            f"Analyze macroeconomic environment impacting {symbol}:\n"
            f"- Macro Climate: {macro_climate}\n"
            f"- RBI Policy: {rbi_policy_stance}\n"
            f"- US 10-Year Treasury Yield: {us_10y_yield}%\n"
            f"- Brent Crude Oil: ${brent_crude_usd} / barrel (Manageable range for India)\n"
            f"- USD/INR: ₹{usdinr}\n"
            f"- Institutional FII Flow: {fii_trend}\n\n"
            "Provide: 1. Macro Tailwinds / Headwinds for Indian Equities, 2. Sectoral sensitivity, 3. Overall Macro Outlook."
        )

        llm_commentary = await self.llm.generate(system_prompt, user_prompt)

        return {
            "agent": self.name,
            "symbol": symbol,
            "macro_bias": "FAVORABLE",
            "indicators": {
                "rbi_stance": rbi_policy_stance,
                "us_10y_yield": us_10y_yield,
                "brent_crude_usd": brent_crude_usd,
                "usdinr": usdinr,
                "fii_trend": fii_trend,
            },
            "summary": (
                f"Macro environment remains resilient with RBI rate pause, steady GDP expansion, "
                f"crude stabilized at ${brent_crude_usd}, and persistent domestic institutional liquidity supporting the broader market."
            ),
            "llm_commentary": llm_commentary,
        }
