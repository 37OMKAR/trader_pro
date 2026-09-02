"""
Market AI — Post-Trade Reflector & Decision Memory Bank
Persists outcomes, maintains a Beta-distribution win-rate estimate per symbol,
and lets Hermes hydrate memory from the DB at startup instead of relying on
process-local state seeded with fictional lessons.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from agents.llm_provider import LLMClient
from packages.market_calendar.calendar import IST_TIMEZONE


# In-process reflection memory. Seeded EMPTY — hydrate_from_records() populates from DB.
_DECISION_MEMORY_BANK: List[Dict[str, Any]] = []


class Reflector:
    """Reflects on closed trades and updates a symbol-level Beta prior for win probability."""

    # Global prior across all symbols/strategies (alpha=wins+1, beta=losses+1)
    _GLOBAL_ALPHA = 1.0
    _GLOBAL_BETA = 1.0

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
        """Store the outcome and synthesize a short lesson."""
        # Update Beta priors (a trade "wins" when raw_return_pct > 0)
        is_win = raw_return_pct > 0
        Reflector._GLOBAL_ALPHA += 1.0 if is_win else 0.0
        Reflector._GLOBAL_BETA += 0.0 if is_win else 1.0

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
        # Reflection lessons are institutional memory — worth LongCat's reasoning depth.
        lesson = await self.llm.generate(system_prompt, user_prompt, force=True, heavy=True)
        if not lesson or len(lesson.strip()) < 10:
            status = "outperformed" if alpha_vs_nifty_pct >= 0 else "underperformed"
            lesson = (
                f"Trade {status} NIFTY 50 with {alpha_vs_nifty_pct:+.2f}% alpha ({exit_reason}). "
                f"Quantitative risk management maintained capital preservation with strict stop adherence."
            )

        entry = {
            "symbol": symbol.upper(),
            "timestamp": datetime.now(IST_TIMEZONE).isoformat(),
            "trade_action": "WIN" if is_win else "LOSS",
            "raw_return_pct": raw_return_pct,
            "alpha_vs_nifty_pct": alpha_vs_nifty_pct,
            "exit_reason": exit_reason,
            "lesson": lesson.strip(),
        }
        _DECISION_MEMORY_BANK.append(entry)
        return entry

    @staticmethod
    def get_recent_reflections(symbol: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        if symbol:
            filtered = [r for r in _DECISION_MEMORY_BANK if r["symbol"] == symbol.upper()]
        else:
            filtered = list(_DECISION_MEMORY_BANK)
        return filtered[-limit:]

    @staticmethod
    def hydrate_from_records(records: List[Dict[str, Any]]) -> int:
        """Populate the memory bank from persisted ReflectionMemoryModel rows.
        Each record must supply symbol, raw_return_pct (or realized_pnl_pct), and lesson.
        Rebuilds Beta priors from the loaded history. Returns the number loaded.
        """
        global _DECISION_MEMORY_BANK
        _DECISION_MEMORY_BANK = []
        Reflector._GLOBAL_ALPHA = 1.0
        Reflector._GLOBAL_BETA = 1.0
        for r in records:
            ret = float(r.get("raw_return_pct", r.get("realized_pnl_pct", 0.0)))
            is_win = ret > 0
            Reflector._GLOBAL_ALPHA += 1.0 if is_win else 0.0
            Reflector._GLOBAL_BETA += 0.0 if is_win else 1.0
            _DECISION_MEMORY_BANK.append({
                "symbol": str(r.get("symbol", "")).upper(),
                "timestamp": str(r.get("timestamp") or r.get("created_at") or ""),
                "trade_action": "WIN" if is_win else "LOSS",
                "raw_return_pct": ret,
                "alpha_vs_nifty_pct": float(r.get("alpha_vs_nifty", r.get("alpha_vs_nifty_pct", 0.0))),
                "exit_reason": str(r.get("exit_reason", "")),
                "lesson": str(r.get("lesson_learned", r.get("lesson", ""))).strip(),
            })
        return len(_DECISION_MEMORY_BANK)

    @staticmethod
    def get_win_prob(symbol: Optional[str] = None, prior_alpha: float = 3.0, prior_beta: float = 3.0) -> float:
        """Beta posterior mean win-probability for a symbol, or global if no symbol given.
        Uses a Beta(prior_alpha, prior_beta) prior to avoid overfitting on tiny samples.
        """
        if symbol:
            rows = [r for r in _DECISION_MEMORY_BANK if r["symbol"] == symbol.upper()]
            wins = sum(1 for r in rows if r.get("raw_return_pct", 0.0) > 0)
            losses = len(rows) - wins
        else:
            wins = int(Reflector._GLOBAL_ALPHA - 1.0)
            losses = int(Reflector._GLOBAL_BETA - 1.0)
        a = prior_alpha + wins
        b = prior_beta + losses
        return round(a / (a + b), 3)

    @staticmethod
    def stats() -> Dict[str, Any]:
        wins = sum(1 for r in _DECISION_MEMORY_BANK if r.get("raw_return_pct", 0.0) > 0)
        total = len(_DECISION_MEMORY_BANK)
        return {
            "trades_recorded": total,
            "wins": wins,
            "losses": total - wins,
            "global_win_prob": Reflector.get_win_prob(),
        }
