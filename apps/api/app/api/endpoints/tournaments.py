"""
Market AI — Strategy Tournaments & Leaderboard REST Endpoints
Orchestrates multi-strategy head-to-head backtest tournaments and StrategyScore rankings.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Query
from services.strategy_dsl.schema import StrategyDefinition, RuleGroup, ConditionRule
from services.tournament_engine.tournament import StrategyTournamentEngine

router = APIRouter(prefix="/tournaments", tags=["Strategy Tournaments"])

tournament_engine = StrategyTournamentEngine()


def get_default_tournament_competitors() -> List[StrategyDefinition]:
    """Pre-loads default candidate strategies for tournaments."""
    return [
        StrategyDefinition(
            strategy_id="RSI_TREND_PULLBACK",
            name="RSI 50-DMA Trend Pullback",
            description="Buys oversold RSI (<42) dips while asset is in strong long-term uptrend above 50-DMA.",
            entry_rules=RuleGroup(
                logical_operator="AND",
                conditions=[
                    ConditionRule(feature="rsi_14", operator="<", threshold=42.0),
                    ConditionRule(feature="close", operator=">", threshold="sma_50"),
                ],
            ),
        ),
        StrategyDefinition(
            strategy_id="VOL_BREAKOUT_ALPHA",
            name="Volume Surge & Relative Alpha Breakout",
            description="Enters on high volume surge (>1.2 z-score) with strong alpha outperformance vs NIFTY 50.",
            entry_rules=RuleGroup(
                logical_operator="AND",
                conditions=[
                    ConditionRule(feature="volume_zscore", operator=">", threshold=1.2),
                    ConditionRule(feature="relative_strength_nifty", operator=">", threshold=55.0),
                    ConditionRule(feature="close", operator=">", threshold="sma_20"),
                ],
            ),
        ),
        StrategyDefinition(
            strategy_id="BOLLINGER_SQUEEZE_REVERSAL",
            name="Bollinger Band Lower Mean Reversion",
            description="Enters on mean-reversion touch of lower Bollinger Band in healthy trending markets.",
            entry_rules=RuleGroup(
                logical_operator="AND",
                conditions=[
                    ConditionRule(feature="close", operator="<=", threshold="bollinger_lower"),
                    ConditionRule(feature="rsi_14", operator=">=", threshold=30.0),
                ],
            ),
        ),
        StrategyDefinition(
            strategy_id="GOLDEN_CROSS_MACD",
            name="Dual Moving Average Golden Cross",
            description="Classic 20-DMA crossing above 50-DMA with positive MACD histogram.",
            entry_rules=RuleGroup(
                logical_operator="AND",
                conditions=[
                    ConditionRule(feature="close", operator=">", threshold="sma_20"),
                    ConditionRule(feature="close", operator=">", threshold="sma_50"),
                ],
            ),
        ),
    ]


@router.get("/leaderboard")
async def get_tournament_leaderboard(asset: str = Query("RELIANCE", description="Target evaluation asset")):
    """Runs tournament across candidate strategies and returns ranked leaderboard with StrategyScores."""
    competitors = get_default_tournament_competitors()
    return await tournament_engine.run_tournament(strategies=competitors, asset=asset)
