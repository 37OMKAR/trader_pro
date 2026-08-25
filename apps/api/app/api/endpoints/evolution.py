"""
Market AI — Autonomous Strategy Evolution REST Endpoints
Critiques backtest weaknesses and generates next-generation strategy mutations.
"""

from typing import Dict, Any, List
from pydantic import BaseModel
from fastapi import APIRouter, Body, HTTPException
from services.strategy_dsl.schema import StrategyDefinition
from services.strategy_evolution.evolution_agent import StrategyEvolutionAgent

router = APIRouter(prefix="/evolution", tags=["Strategy Evolution"])

evolution_agent = StrategyEvolutionAgent()


class EvolutionRequest(BaseModel):
    strategy: StrategyDefinition
    backtest_result: Dict[str, Any]


@router.post("/evolve")
async def evolve_strategy(req: EvolutionRequest):
    """Critiques strategy backtest metrics and breeds an evolved next-generation DSL strategy."""
    return evolution_agent.critique_and_evolve(
        strategy=req.strategy,
        backtest_result=req.backtest_result,
    )
