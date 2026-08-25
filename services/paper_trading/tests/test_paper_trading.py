"""
Unit tests for Paper Trading Account and Order Matcher.
"""

import pytest
from services.paper_trading.account import PaperTradingAccount


def test_paper_trading_buy_sell_lifecycle():
    account = PaperTradingAccount(account_id="TEST_ACC", initial_capital=500_000.0)

    # 1. Place Buy Order
    res_buy = account.place_order(
        symbol="RELIANCE",
        action="BUY",
        quantity=50,
        market_price=2500.0,
    )
    assert res_buy["status"] == "FILLED"
    assert "RELIANCE" in account.positions
    assert account.positions["RELIANCE"]["quantity"] == 50
    assert account.cash_balance < 500_000.0

    # 2. Portfolio Valuation
    summary = account.get_portfolio_summary(current_quotes={"RELIANCE": 2600.0})
    assert summary["unrealized_pnl"] > 0
    assert summary["total_portfolio_value"] > 500_000.0

    # 3. Place Sell Order
    res_sell = account.place_order(
        symbol="RELIANCE",
        action="SELL",
        quantity=50,
        market_price=2600.0,
    )
    assert res_sell["status"] == "FILLED"
    assert "RELIANCE" not in account.positions
    assert account.realized_pnl > 0
    assert len(account.trade_history) == 2
