"""
Unit tests for Quantitative Backtest Engine.
"""

import pytest
from packages.market_data.development_provider import DevelopmentMarketDataProvider
from services.strategy_dsl.schema import StrategyDefinition, RuleGroup, ConditionRule
from services.backtest_engine.engine import BacktestEngine


@pytest.mark.anyio
async def test_backtest_execution():
    provider = DevelopmentMarketDataProvider()
    engine = BacktestEngine()

    candles = await provider.get_history("RELIANCE", timeframe="1D", limit=60)

    strategy = StrategyDefinition(
        strategy_id="RSI_TREND_V1",
        name="RSI Trend Breakout",
        description="Simple trend strategy",
        asset_universe=["RELIANCE"],
        entry_rules=RuleGroup(
            logical_operator="AND",
            conditions=[
                ConditionRule(feature="rsi_14", operator=">", threshold=50.0),
                ConditionRule(feature="close", operator=">", threshold="sma_20"),
            ],
        ),
    )

    result = engine.run_backtest(strategy, candles, initial_capital=500_000.0)

    assert result["run_id"].startswith("BT-RSI_TREND_V1")
    assert "metrics" in result
    assert "total_return_pct" in result["metrics"]
    assert "sharpe_ratio" in result["metrics"]
    assert "max_drawdown_pct" in result["metrics"]
    assert len(result["equity_curve"]) > 0
