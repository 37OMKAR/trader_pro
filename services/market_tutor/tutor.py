"""
Market AI — Dalal Street AI Market Tutor
Interactive quantitative and conceptual mentor explaining Indian equity mechanics, derivatives, risk management, and trading systems.
"""

from typing import Dict, Any, List
from agents.llm_provider import LLMClient


class MarketTutor:
    """Specialized AI tutor for Indian stock markets, algorithmic trading, and derivatives concepts."""

    def __init__(self):
        self.llm = LLMClient()

    async def answer_question(self, question: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        system_prompt = (
            "You are the Dalal Street Market AI Tutor, an elite veteran trader and quantitative finance educator. "
            "You explain complex Indian market concepts clearly, using practical examples, formula breakdowns, "
            "and institutional risk rules. You cover NSE/BSE rules, Option Greeks, India VIX, STT, SEBI guidelines, "
            "and algorithmic trading strategies."
        )

        user_prompt = f"User Question: {question}\n\nProvide a structured, engaging, and authoritative explanation."

        response = await self.llm.generate(system_prompt, user_prompt)

        return {
            "question": question,
            "response": response,
            "suggested_followups": [
                "How does India VIX impact option premiums and Kelly position sizing?",
                "What is the difference between Weekly Thursday expiry and Monthly expiry?",
                "How does STT and regulatory slippage affect intraday strategy profitability?",
            ],
        }
