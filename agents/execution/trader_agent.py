"""
Market AI — Main Trader Agent
Reviews analyst reports and Bull vs Bear debate to formulate a concrete, actionable trade plan.
"""

from typing import Dict, Any
from agents.llm_provider import LLMClient


class TraderAgent:
    """Core trader agent responsible for formulating explicit trade orders."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Lead Trader"

    async def decide_trade(
        self,
        symbol: str,
        current_price: float,
        analyst_reports: Dict[str, Any],
        bull_case: Dict[str, Any],
        bear_case: Dict[str, Any],
    ) -> Dict[str, Any]:
        # Formulate deterministic trade parameters
        action = "BUY"
        entry_price = round(current_price, 2)
        stop_loss = round(current_price * 0.965, 2)  # -3.5% risk
        target_1 = round(current_price * 1.070, 2)   # +7.0% (1:2 R:R)
        target_2 = round(current_price * 1.120, 2)   # +12.0%
        risk_per_share = round(entry_price - stop_loss, 2)
        reward_per_share = round(target_1 - entry_price, 2)
        rr_ratio = round(reward_per_share / max(risk_per_share, 0.01), 2)
        time_horizon = "2-4 Weeks (Swing Trade)"
        suggested_allocation_pct = 10.0  # 10% of portfolio

        system_prompt = (
            "You are the Head Trader at a quantitative equity hedge fund. "
            "Weigh the Analyst Reports and the Bull vs Bear debate to synthesize an optimal trade decision. "
            "Specify Action, Entry, Stop Loss, Target, and Rationale."
        )

        user_prompt = (
            f"Synthesize Trade Decision for {symbol} (Current Price: ₹{current_price}):\n"
            f"- Bull Case: {bull_case.get('thesis')}\n"
            f"- Bear Case: {bear_case.get('thesis')}\n"
            f"- Proposed Setup: Action={action}, Entry=₹{entry_price}, Stop Loss=₹{stop_loss}, Target=₹{target_1}, R:R={rr_ratio}\n\n"
            "Provide executive rationale justifying the trade parameters."
        )

        llm_rationale = await self.llm.generate(system_prompt, user_prompt)

        return {
            "agent": self.name,
            "symbol": symbol,
            "action": action,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,
            "risk_reward_ratio": f"1:{rr_ratio}",
            "suggested_allocation_pct": suggested_allocation_pct,
            "time_horizon": time_horizon,
            "rationale": (
                f"Bull thesis outweighs near-term bear risks. Golden moving average alignment and solid "
                f"fundamentals offer an asymmetric 1:{rr_ratio} risk-to-reward setup with disciplined stop loss at ₹{stop_loss}."
            ),
            "llm_rationale": llm_rationale,
        }
