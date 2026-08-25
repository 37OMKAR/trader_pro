"""
Market AI — Strategy Tournament Engine
Runs parallel multi-strategy tournaments, evaluates StrategyScores, and produces ranked leaderboards.
"""

from typing import List, Dict, Any, Optional
from services.strategy_dsl.schema import StrategyDefinition
from services.backtest_engine.engine import BacktestEngine
from services.tournament_engine.scorer import StrategyScorer
from packages.market_data.development_provider import DevelopmentMarketDataProvider


class StrategyTournamentEngine:
    """Orchestrates head-to-head backtest tournaments across strategy candidates."""

    def __init__(self):
        self.backtest_engine = BacktestEngine()
        self.market_provider = DevelopmentMarketDataProvider()

    async def run_tournament(
        self,
        strategies: List[StrategyDefinition],
        asset: str = "RELIANCE",
        initial_capital: float = 1_000_000.0,
    ) -> Dict[str, Any]:
        """Runs all strategies on the target asset, computes StrategyScores, and sorts leaderboard."""
        candles = await self.market_provider.get_history(asset.upper(), timeframe="1D", limit=80)
        
        entries = []
        for strat in strategies:
            try:
                bt_res = self.backtest_engine.run_backtest(
                    strategy=strat,
                    candles=candles,
                    initial_capital=initial_capital,
                )
                score_info = StrategyScorer.calculate_strategy_score(bt_res["metrics"])
                
                entries.append({
                    "strategy_id": strat.strategy_id,
                    "name": strat.name,
                    "description": strat.description,
                    "asset": asset,
                    "strategy_score": score_info["strategy_score"],
                    "badge": score_info["badge"],
                    "tier": score_info["tier"],
                    "sub_scores": score_info["sub_scores"],
                    "metrics": bt_res["metrics"],
                    "trades_count": len(bt_res["trades"]),
                })
            except Exception as e:
                continue

        # Sort entries by StrategyScore descending
        entries.sort(key=lambda x: x["strategy_score"], reverse=True)

        # Assign rank
        for idx, entry in enumerate(entries, start=1):
            entry["rank"] = idx

        return {
            "tournament_name": f"Institutional Alpha Tournament ({asset})",
            "evaluated_asset": asset,
            "total_competitors": len(entries),
            "leaderboard": entries,
        }
