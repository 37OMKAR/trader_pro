"""
Market AI — Aggressive Risk Debator
Advocates for maximizing alpha, widening stop-loss buffers on high-conviction breakout setups, and capturing asymmetric upside.
"""

from typing import Dict, Any
from agents.llm_provider import LLMClient


class AggressiveRiskDebator:
    """Specialist debator championing growth capture and risk-tolerant execution."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Aggressive Risk Debator"

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
            "You are the Aggressive Risk Analyst at a quantitative trading desk. "
            "Your role is to argue for higher position sizing, wider stop-loss leeway to prevent premature stop-outs, "
            "and capturing maximum upside momentum in favorable market regimes."
        )

        user_prompt = (
            f"Review trade for {symbol} in {market_regime} regime:\n"
            f"- Entry: ₹{entry}, Target: ₹{target}, Stop: ₹{stop}\n\n"
            "Argue why this trade should be sized aggressively (up to 15-20% capital allocation) "
            "and why the stop-loss should give the asset breathing room."
        )

        llm_arg = await self.llm.generate(system_prompt, user_prompt)

        return {
            "agent": self.name,
            "stance": "MAX_GROWTH",
            "recommended_allocation_pct": 18.0,
            "stop_loss_leeway": "WIDER (+1.5% buffer)",
            "argument": (
                f"In the current {market_regime} regime, {symbol} possesses strong upside momentum. "
                f"Cutting position size or setting too tight a stop risks being whipsawed on routine intraday volatility. "
                f"We should allocate an aggressive 15-18% of available margin to compound returns."
            ),
            "llm_commentary": llm_arg,
        }
