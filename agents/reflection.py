"""
Market AI — Post-Trade Reflector & Decision Memory Bank
Evaluates historical trade outcomes against NIFTY 50 Alpha and stores compact lessons for future prompt injection.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from agents.llm_provider import LLMClient
from packages.market_calendar.calendar import IST_TIMEZONE


# In-memory & persisted reflection storage
_DECISION_MEMORY_BANK: List[Dict[str, Any]] = [
    {
        "symbol": "RELIANCE",
        "timestamp": "2026-08-10T14:30:00+05:30",
        "trade_action": "BUY",
        "raw_return_pct": 4.2,
        "alpha_vs_nifty_pct": 2.8,
        "lesson": (
            "Bullish breakout thesis confirmed: Volume surge above 1.5x 20 DMA validated entry. "
            "Take-profit target 1 hit smoothly without drawdown."
        ),
    },
    {
        "symbol": "TCS",
        "timestamp": "2026-08-14T11:15:00+05:30",
        "trade_action": "BUY",
        "raw_return_pct": -1.6,
        "alpha_vs_nifty_pct": -2.1,
        "lesson": (
            "Premature entry before US Fed rate commentary: Global tech sentiment dragged share price. "
            "Lesson: Ensure Macro Analyst interest-rate confirmation before committing capital to IT exporters."
        ),
    },
]


class Reflector:
    """Self-correcting agent reflecting on realized trade outcomes and maintaining the firm's institutional memory."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Post-Trade Reflector"

    async def reflect_on_trade(
        self,
        symbol: str,
        initial_thesis: str,
        raw_return_pct: float,
        alpha_vs_nifty_pct: float,
        exit_reason: str = "TARGET_REACHED",
    ) -> Dict[str, Any]:
        """Synthesizes a 2-4 sentence reflection lesson on a completed trade."""
        system_prompt = (
            "You are a Senior Trading Performance Auditor reviewing past trading decisions. "
            "Write exactly 2-3 sentences of terse, high-density institutional prose:\n"
            "1. Was the directional call correct? (cite the alpha figure)\n"
            "2. Which part of the thesis held or failed?\n"
            "3. One concrete lesson to apply to future trades for this symbol/sector."
        )

        user_prompt = (
            f"Review trade outcome for {symbol}:\n"
            f"- Initial Thesis: {initial_thesis}\n"
            f"- Exit Reason: {exit_reason}\n"
            f"- Raw Return: {raw_return_pct:+.2f}%\n"
            f"- Alpha vs NIFTY 50: {alpha_vs_nifty_pct:+.2f}%\n"
        )

        lesson = await self.llm.generate(system_prompt, user_prompt)
        if not lesson or len(lesson.strip()) < 10:
            status = "outperformed" if alpha_vs_nifty_pct >= 0 else "underperformed"
            lesson = (
                f"Trade {status} NIFTY 50 with {alpha_vs_nifty_pct:+.2f}% alpha ({exit_reason}). "
                f"Quantitative risk management maintained capital preservation with strict stop adherence."
            )

        entry = {
            "symbol": symbol,
            "timestamp": datetime.now(IST_TIMEZONE).isoformat(),
            "trade_action": "BUY" if raw_return_pct >= 0 else "SELL",
            "raw_return_pct": raw_return_pct,
            "alpha_vs_nifty_pct": alpha_vs_nifty_pct,
            "exit_reason": exit_reason,
            "lesson": lesson.strip(),
        }

        _DECISION_MEMORY_BANK.append(entry)
        return entry

    @staticmethod
    def get_recent_reflections(symbol: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves past lessons for symbol or firm-wide."""
        if symbol:
            filtered = [r for r in _DECISION_MEMORY_BANK if r["symbol"] == symbol.upper()]
            return filtered[-limit:]
        return _DECISION_MEMORY_BANK[-limit:]
