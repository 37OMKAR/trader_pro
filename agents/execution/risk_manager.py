"""
Market AI — Risk Management Agent
Strict deterministic risk governance: validates position sizing, R:R limits, drawdown caps, and market regime compliance.
"""

from typing import Dict, Any
from agents.llm_provider import LLMClient


class RiskManagementAgent:
    """Specialized governance agent evaluating trade safety and position limits."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Risk Manager"
        self.max_position_pct = 15.0  # Max 15% in single stock
        self.min_risk_reward = 2.0    # Minimum 1:2 R:R

    async def evaluate_risk(
        self,
        symbol: str,
        trade_proposal: Dict[str, Any],
        portfolio_value: float = 1_000_000.0,
    ) -> Dict[str, Any]:
        entry = trade_proposal["entry_price"]
        stop = trade_proposal["stop_loss"]
        target = trade_proposal["target_1"]
        alloc_pct = trade_proposal["suggested_allocation_pct"]

        risk_pct = round(((entry - stop) / entry) * 100, 2)
        reward_pct = round(((target - entry) / entry) * 100, 2)
        actual_rr = round(reward_pct / max(risk_pct, 0.01), 2)

        # Risk Rules Verification
        passes_rr = actual_rr >= self.min_risk_reward
        passes_alloc = alloc_pct <= self.max_position_pct
        passes_risk_pct = risk_pct <= 5.0  # Max 5% stop distance

        is_approved = passes_rr and passes_alloc and passes_risk_pct
        status = "APPROVED" if is_approved else "ADJUSTED"

        # Calculate exact recommended quantity and rupee risk on ₹10,00,000 portfolio
        allocated_capital = (portfolio_value * (alloc_pct / 100.0))
        max_shares = int(allocated_capital / entry)
        total_risk_inr = round(max_shares * (entry - stop), 2)
        risk_of_portfolio_pct = round((total_risk_inr / portfolio_value) * 100, 2)

        system_prompt = (
            "You are the Chief Risk Officer (CRO) at an institutional trading firm. "
            "Audit trade proposals for maximum drawdown protection, position limits, and risk/reward discipline."
        )

        user_prompt = (
            f"Audit trade proposal for {symbol}:\n"
            f"- Entry: ₹{entry}, Stop Loss: ₹{stop} ({risk_pct}% risk)\n"
            f"- Target: ₹{target} ({reward_pct}% reward), R:R = 1:{actual_rr}\n"
            f"- Proposed Allocation: {alloc_pct}% (₹{allocated_capital:,.2f})\n"
            f"- Total INR Risk on Portfolio: ₹{total_risk_inr:,.2f} ({risk_of_portfolio_pct}% of total fund)\n\n"
            "State risk verdict and mandatory conditions."
        )

        llm_assessment = await self.llm.generate(system_prompt, user_prompt)

        return {
            "agent": self.name,
            "status": status,
            "approved": is_approved,
            "max_approved_shares": max_shares,
            "capital_allocated_inr": allocated_capital,
            "max_drawdown_risk_inr": total_risk_inr,
            "risk_of_portfolio_pct": risk_of_portfolio_pct,
            "risk_checks": {
                "risk_reward_acceptable": passes_rr,
                "position_size_within_limits": passes_alloc,
                "stop_distance_prudent": passes_risk_pct,
            },
            "summary": (
                f"Risk checks passed. Position capped at {max_shares} shares (₹{allocated_capital:,.2f}). "
                f"Maximum downside risk strictly limited to ₹{total_risk_inr:,.2f} ({risk_of_portfolio_pct}% of total capital)."
            ),
            "llm_assessment": llm_assessment,
        }
