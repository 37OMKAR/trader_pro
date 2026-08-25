"""
Unit tests for Autonomous Strategy Evolution Agent.
"""

import pytest
from services.strategy_dsl.schema import StrategyDefinition, RuleGroup, ConditionRule
from services.strategy_evolution.evolution_agent import StrategyEvolutionAgent


def test_strategy_evolution_critique_and_mutation():
    agent = StrategyEvolutionAgent()

    strategy = StrategyDefinition(
        strategy_id="RSI_TREND_V1",
        name="RSI Momentum V1",
        description="Initial generation strategy",
        version="1.0.0",
        entry_rules=RuleGroup(
            logical_operator="AND",
            conditions=[ConditionRule(feature="rsi_14", operator="<", threshold=45.0)],
        ),
    )

    # Sub-optimal backtest results (High drawdown, low win rate)
    mock_backtest = {
        "metrics": {
            "cagr_pct": 8.0,
            "sharpe_ratio": 0.8,
            "max_drawdown_pct": 14.5,
            "win_rate_pct": 42.0,
            "profit_factor": 1.2,
        },
        "trades": [],
    }

    evolution_result = agent.critique_and_evolve(strategy, mock_backtest)

    assert evolution_result["parent_strategy_id"] == "RSI_TREND_V1"
    assert evolution_result["mutated_version"] == "1.1.0"
    assert len(evolution_result["critique"]) >= 1
    assert len(evolution_result["mutations_applied"]) >= 1

    mutated = evolution_result["mutated_strategy"]
    assert mutated.version == "1.1.0"
    # Stop loss should be tightened due to high drawdown
    assert mutated.risk_management.stop_loss_pct < strategy.risk_management.stop_loss_pct
