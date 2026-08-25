"""
Unit tests for Strategy Rule DSL Schema and Evaluator.
"""

import pytest
from services.strategy_dsl.schema import StrategyDefinition, RuleGroup, ConditionRule
from services.strategy_dsl.evaluator import DSLEvaluator


def test_dsl_rule_evaluation():
    strategy = StrategyDefinition(
        strategy_id="RSI_MOMENTUM_PULLBACK",
        name="RSI Momentum Pullback",
        description="Buys oversold bounce above 50-DMA",
        entry_rules=RuleGroup(
            logical_operator="AND",
            conditions=[
                ConditionRule(feature="rsi_14", operator="<", threshold=40.0),
                ConditionRule(feature="close", operator=">", threshold="sma_50"),
            ],
        ),
    )

    # Scenario 1: Entry conditions met
    features_bullish = {
        "rsi_14": 35.0,
        "close": 2500.0,
        "sma_50": 2400.0,
    }
    assert DSLEvaluator.should_enter_trade(strategy, features_bullish) is True

    # Scenario 2: Entry conditions failed (RSI too high)
    features_overbought = {
        "rsi_14": 65.0,
        "close": 2500.0,
        "sma_50": 2400.0,
    }
    assert DSLEvaluator.should_enter_trade(strategy, features_overbought) is False
