"""
Market AI — Portfolio Manager Agent
Final executive authorization, simulated trade routing, and portfolio capital management.
"""

from datetime import datetime
from typing import Dict, Any
from agents.llm_provider import LLMClient


class PortfolioManagerAgent:
    """Executive portfolio manager giving final trade authorization and portfolio governance."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Portfolio Manager"

    async def authorize_trade(
        self,
        symbol: str,
        trader_proposal: Dict[str, Any],
        risk_evaluation: Dict[str, Any],
        current_portfolio: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not risk_evaluation.get("approved", False):
            return {
                "agent": self.name,
                "status": "REJECTED_BY_RISK",
                "trade_executed": False,
                "reason": "Failed risk checks.",
            }

        shares = risk_evaluation["max_approved_shares"]
        price = trader_proposal["entry_price"]
        total_cost = round(shares * price, 2)
        cash_balance = current_portfolio.get("cash", 1_000_000.0)

        if total_cost > cash_balance:
            shares = int(cash_balance * 0.95 / price)
            total_cost = round(shares * price, 2)

        system_prompt = (
            "You are the Chief Investment Officer (CIO) / Lead Portfolio Manager. "
            "Deliver the final executive authorization decision for trade execution."
        )

        user_prompt = (
            f"Final Trade Authorization for {symbol}:\n"
            f"- Action: {trader_proposal['action']} {shares} shares @ ₹{price}\n"
            f"- Total Investment: ₹{total_cost:,.2f}\n"
            f"- Target 1: ₹{trader_proposal['target_1']} | Stop Loss: ₹{trader_proposal['stop_loss']}\n"
            f"- Risk Clearance: {risk_evaluation.get('summary')}\n\n"
            "Issue executive authorization memo."
        )

        llm_memo = await self.llm.generate(system_prompt, user_prompt)

        return {
            "agent": self.name,
            "status": "EXECUTED_IN_PAPER_PORTFOLIO",
            "trade_executed": True,
            "order_details": {
                "symbol": symbol,
                "action": trader_proposal["action"],
                "quantity": shares,
                "entry_price": price,
                "total_cost_inr": total_cost,
                "stop_loss": trader_proposal["stop_loss"],
                "target_1": trader_proposal["target_1"],
                "target_2": trader_proposal["target_2"],
                "executed_at": datetime.now().isoformat(),
            },
            "portfolio_impact": {
                "previous_cash": cash_balance,
                "new_cash": round(cash_balance - total_cost, 2),
                "allocated_percentage": round((total_cost / current_portfolio.get("total_value", 1_000_000.0)) * 100, 2),
            },
            "executive_memo": (
                f"Trade APPROVED & EXECUTED. Purchased {shares} shares of {symbol} at ₹{price} "
                f"(Total: ₹{total_cost:,.2f}). Profit targets set at ₹{trader_proposal['target_1']} / ₹{trader_proposal['target_2']} "
                f"with automated protective stop loss at ₹{trader_proposal['stop_loss']}."
            ),
            "llm_memo": llm_memo,
        }
