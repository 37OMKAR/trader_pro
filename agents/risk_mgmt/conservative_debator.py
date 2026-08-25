"""
Market AI — Conservative Risk Debator
Advocates for strict capital preservation, tail-risk defense, drawdown limits, and tight trailing stops.
"""

from typing import Dict, Any
from agents.llm_provider import LLMClient


class ConservativeRiskDebator:
    """Specialist debator championing capital preservation and maximum drawdown defense."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Conservative Risk Debator"

    async def argue(
        self,
        symbol: str,
        trade_proposal: Dict[str, Any],
        market_regime: str = "BULL",
    ) -> Dict[str, Any]:
        entry = trade_proposal.get("entry_price", 1000.0)
        target = trade_proposal.get("target_1", entry * 1.05)
        stop = trade_proposal.get("stop_loss", entry * 0.98)

        system_prompt = (
            "You are the Conservative Risk Guardian at an institutional trading firm. "
            "Your priority is capital preservation, eliminating black-swan downside exposure, "
            "and ensuring strict position sizing caps (5-8% max) with rigid stop-loss discipline."
        )

        user_prompt = (
            f"Audit trade for {symbol} under {market_regime} conditions:\n"
            f"- Entry: ₹{entry}, Target: ₹{target}, Stop: ₹{stop}\n\n"
            "Argue for risk reduction, capping position size to 5-8%, and enforcing a strict stop loss."
        )

        llm_arg = await self.llm.generate(system_prompt, user_prompt)

        return {
            "agent": self.name,
            "stance": "CAPITAL_PRESERVATION",
            "recommended_allocation_pct": 7.5,
            "stop_loss_leeway": "STRICT_TIGHT",
            "argument": (
                f"Capital preservation is our primary imperative. Sudden global macro shifts or sector rotation "
                f"could trigger immediate drawdown on {symbol}. Total portfolio exposure must not exceed 7.5%, "
                f"and stop-loss must be executed mechanically without emotional leeway."
            ),
            "llm_commentary": llm_arg,
        }
