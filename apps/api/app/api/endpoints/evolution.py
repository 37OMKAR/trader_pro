"""
Market AI — Autonomous Strategy Evolution REST Endpoints
Critiques backtest weaknesses and generates next-generation strategy mutations.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Body, HTTPException
from services.strategy_dsl.schema import StrategyDefinition
from services.strategy_evolution.evolution_agent import StrategyEvolutionAgent
from services.backtest_engine.engine import BacktestEngine
from packages.market_data.development_provider import DevelopmentMarketDataProvider

router = APIRouter(prefix="/evolution", tags=["Strategy Evolution"])

evolution_agent = StrategyEvolutionAgent()
_backtest_engine = BacktestEngine()
_market_provider = DevelopmentMarketDataProvider()


class EvolutionRequest(BaseModel):
    """Accepts the full {strategy, backtest_result} shape OR the short web form
    `{symbol, generations}` — in the short form the server runs a quick baseline
    backtest first and uses that as the critique input.
    """
    strategy: Optional[Dict[str, Any]] = None
    backtest_result: Optional[Dict[str, Any]] = None
    symbol: Optional[str] = None
    generations: int = 1


@router.post("/evolve")
async def evolve_strategy(req: EvolutionRequest = Body(...)):
    """Critique strategy backtest metrics and breed an evolved next-generation DSL strategy."""
    if req.strategy and req.backtest_result:
        try:
            strategy = StrategyDefinition(**req.strategy) if isinstance(req.strategy, dict) else req.strategy
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid strategy: {exc}")
        return evolution_agent.critique_and_evolve(strategy=strategy, backtest_result=req.backtest_result)

    # Short-form: build a baseline strategy for `symbol`, backtest it, then evolve.
    symbol = (req.symbol or "RELIANCE").upper()
    baseline = StrategyDefinition(
        strategy_id=f"BASELINE_{symbol}",
        name=f"Baseline trend for {symbol}",
        description="Server-generated baseline used because the client did not supply a full strategy.",
        entry_rules={
            "logical_operator": "AND",
            "conditions": [{"feature": "close", "operator": ">", "threshold": "sma_20"}],
        },
        risk_management={"stop_loss_pct": 2.5, "take_profit_pct": 6.0},
    )
    candles = await _market_provider.get_history(symbol, timeframe=baseline.timeframe, limit=80)
    bt = _backtest_engine.run_backtest(strategy=baseline, candles=candles, initial_capital=1_000_000.0)
    return evolution_agent.critique_and_evolve(strategy=baseline, backtest_result=bt)
