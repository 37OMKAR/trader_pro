"""
Market AI — Paper Trading Order Matcher & Execution Simulator
Simulates realistic trade fills with bid-ask spread, slippage, and Indian regulatory fees.
"""

from typing import Dict, Any, Tuple
from services.backtest_engine.engine import BacktestEngine


class PaperOrderMatcher:
    """Executes paper orders with realistic slippage and fee deduction."""

    @staticmethod
    def calculate_fees(traded_value: float, is_buy: bool) -> float:
        """Calculates Indian regulatory and broker transaction costs."""
        return BacktestEngine.calculate_indian_transaction_cost(traded_value, is_buy=is_buy)

    @classmethod
    def match_order(
        cls,
        action: str,  # "BUY" or "SELL"
        symbol: str,
        quantity: int,
        market_price: float,
        order_type: str = "MARKET",
        limit_price: float = 0.0,
        slippage_pct: float = 0.05,
    ) -> Tuple[bool, float, float, str]:
        """
        Executes order and returns: (success, fill_price, fee_inr, status_message)
        """
        action = action.upper()
        if quantity <= 0 or market_price <= 0:
            return False, 0.0, 0.0, "Invalid quantity or market price."

        # Limit order condition
        if order_type.upper() == "LIMIT":
            if action == "BUY" and market_price > limit_price:
                return False, 0.0, 0.0, f"Limit price ₹{limit_price} is below market price ₹{market_price}."
            if action == "SELL" and market_price < limit_price:
                return False, 0.0, 0.0, f"Limit price ₹{limit_price} is above market price ₹{market_price}."

        # Apply slippage
        if action == "BUY":
            fill_price = round(market_price * (1.0 + (slippage_pct / 100.0)), 2)
        else:
            fill_price = round(market_price * (1.0 - (slippage_pct / 100.0)), 2)

        traded_value = fill_price * quantity
        fee = cls.calculate_fees(traded_value, is_buy=(action == "BUY"))

        return True, fill_price, fee, f"Filled {quantity} shares of {symbol} at ₹{fill_price} (Fee: ₹{fee})"
