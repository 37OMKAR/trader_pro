"""
Unit tests for Strategy Scorer and Tournament Engine.
"""

import pytest
from services.strategy_dsl.schema import StrategyDefinition, RuleGroup, ConditionRule
from services.tournament_engine.scorer import StrategyScorer
from services.tournament_engine.tournament import StrategyTournamentEngine


def test_strategy_scorer_calculation():
    mock_metrics = {
        "cagr_pct": 22.5,
        "sharpe_ratio": 2.1,
        "max_drawdown_pct": 8.5,
        "win_rate_pct": 62.0,
        "profit_factor": 2.2,
    }
    score_data = StrategyScorer.calculate_strategy_score(mock_metrics)

    assert score_data["strategy_score"] >= 75.0
    assert score_data["badge"] in ["ELITE_ALPHA", "BALANCED_ALL_WEATHER"]
    assert "return_score" in score_data["sub_scores"]


@pytest.mark.anyio
async def test_tournament_execution():
    tournament = StrategyTournamentEngine()

    strat1 = StrategyDefinition(
        strategy_id="RSI_TREND",
        name="RSI Momentum",
        description="RSI breakout above 50",
        entry_rules=RuleGroup(
            logical_operator="AND",
            conditions=[ConditionRule(feature="rsi_14", operator=">", threshold=50.0)],
        ),
    )
    strat2 = StrategyDefinition(
        strategy_id="SMA_CROSS",
        name="SMA Trend",
        description="Close above 20-DMA",
        entry_rules=RuleGroup(
            logical_operator="AND",
            conditions=[ConditionRule(feature="close", operator=">", threshold="sma_20")],
        ),
    )

    res = await tournament.run_tournament([strat1, strat2], asset="RELIANCE")

    assert res["total_competitors"] >= 1
    assert "leaderboard" in res
    assert len(res["leaderboard"]) >= 1
    assert res["leaderboard"][0]["rank"] == 1
