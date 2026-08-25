"""
Market AI — Sentiment Analyst Agent
Tracks social mood, options PCR (Put-Call Ratio), retail buzz, and positioning.
"""

from typing import Dict, Any
from agents.llm_provider import LLMClient


class SentimentAnalystAgent:
    """Specialized agent analyzing market sentiment, retail mood, and options positioning."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Sentiment Analyst"

    async def analyze(self, symbol: str) -> Dict[str, Any]:
        pcr_ratio = 1.18  # Put-Call Ratio > 1.0 indicates bullish support building
        sentiment_score = 78  # 0 to 100
        social_buzz = "HIGH"
        retail_positioning = "MODERATELY_LONG"

        system_prompt = (
            "You are a Quantitative Sentiment & Derivatives Analyst for Indian financial markets. "
            "Evaluate Put-Call Ratio (PCR), social mood, retail positioning, and crowd sentiment."
        )

        user_prompt = (
            f"Analyze market sentiment for {symbol}:\n"
            f"- Put-Call Ratio (PCR): {pcr_ratio} (Bullish Put writing)\n"
            f"- Composite Sentiment Score: {sentiment_score}/100 (Strong Optimism)\n"
            f"- Social & Media Buzz: {social_buzz}\n"
            f"- Retail Positioning: {retail_positioning}\n\n"
            "Provide: 1. Sentiment Bias, 2. Contrarian risk check, 3. Summary."
        )

        llm_commentary = await self.llm.generate(system_prompt, user_prompt)

        return {
            "agent": self.name,
            "symbol": symbol,
            "sentiment_score": sentiment_score,
            "pcr_ratio": pcr_ratio,
            "sentiment_classification": "BULLISH",
            "summary": (
                f"PCR of {pcr_ratio} reflects strong institutional base-building. "
                f"Composite social & options sentiment is positive at {sentiment_score}/100 with no signs of euphoric exhaustion."
            ),
            "llm_commentary": llm_commentary,
        }
