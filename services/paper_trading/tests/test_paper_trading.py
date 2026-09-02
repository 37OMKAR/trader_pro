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


def test_paper_trading_tick_fires_target_and_stop():
    account = PaperTradingAccount(account_id="TEST_TICK", initial_capital=1_000_000.0)

    # Enter two positions with explicit stop/target.
    account.place_order(symbol="AAA", action="BUY", quantity=100, market_price=100.0,
                        stop_loss=95.0, target=110.0)
    account.place_order(symbol="BBB", action="BUY", quantity=100, market_price=200.0,
                        stop_loss=190.0, target=220.0)

    # Bar 1: AAA rallies past target; BBB drifts sideways.
    exits = account.tick({
        "AAA": {"high": 112.0, "low": 101.0, "close": 111.0},
        "BBB": {"high": 205.0, "low": 198.0, "close": 202.0},
    })
    assert len(exits) == 1
    assert exits[0]["symbol"] == "AAA"
    assert exits[0]["exit_reason"] == "PROFIT_TARGET_HIT"
    assert exits[0]["price"] == 110.0
    assert "AAA" not in account.positions
    assert "BBB" in account.positions

    # Bar 2: BBB crashes through the stop.
    exits = account.tick({"BBB": {"high": 199.0, "low": 188.0, "close": 189.0}})
    assert len(exits) == 1
    assert exits[0]["symbol"] == "BBB"
    assert exits[0]["exit_reason"] == "STOP_LOSS_HIT"
    assert exits[0]["price"] == 190.0
    assert "BBB" not in account.positions
    assert account.realized_pnl != 0.0
