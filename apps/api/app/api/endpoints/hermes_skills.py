"""
Market AI — Agentskills.io skill surface for external agent frameworks (e.g. Nous hermes-agent).
Six endpoints, one per skill. Each endpoint is a thin adapter over already-tested internals.
Auth: bearer token in HERMES_SKILL_TOKEN env var. Rejects if unset or wrong.
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
import os
from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel, Field

from agents.hermes_brain import HermesSupervisorBrain
from agents.execution.portfolio_manager import PortfolioManagerAgent
from agents.llm_provider import LLMClient
from services.paper_trading.account import PaperTradingAccount
from services.strategy_evolution.evolution_agent import StrategyEvolutionAgent
from services.tournament_engine.tournament import StrategyTournamentEngine
from services.backtest_engine.engine import BacktestEngine
from packages.market_data.yahoo_provider import YahooFinanceMarketDataProvider
from ops import config as ops_config
from ops import state as ops_state
from services.reporting.digest import format_end_of_day

router = APIRouter(prefix="/skills/trading", tags=["Skills (agentskills.io)"])

# Single process-wide paper account for the skill surface.
_ACCOUNT = PaperTradingAccount(
    account_id="HERMES_SKILL_ACC",
    name="Hermes Skill Fund",
    initial_capital=1_000_000.0,
)
_HERMES = HermesSupervisorBrain()
_PM = PortfolioManagerAgent(LLMClient())
_PROVIDER = YahooFinanceMarketDataProvider()
_EVOLUTION = StrategyEvolutionAgent()
_TOURNAMENT = StrategyTournamentEngine()


def _auth(authorization: Optional[str]) -> None:
    """Bearer-token auth. When HERMES_SKILL_TOKEN is unset, refuses all calls (fail closed)."""
    token = os.getenv("HERMES_SKILL_TOKEN", "").strip()
    if not token:
        raise HTTPException(status_code=503, detail="HERMES_SKILL_TOKEN not configured; skill surface disabled.")
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    if authorization.split(None, 1)[1].strip() != token:
        raise HTTPException(status_code=403, detail="Invalid token")


# ---------- Schemas ----------

class DeliberateRequest(BaseModel):
    symbol: str
    portfolio_value: float = 1_000_000.0
    conduct_web_research: bool = False


class PlaceOrderRequest(BaseModel):
    symbol: str
    action: str = Field(pattern="^(BUY|SELL)$")
    quantity: int = Field(gt=0)
    entry_price: float = Field(gt=0)
    stop_loss: Optional[float] = None
    target: Optional[float] = None


class EvolveRequest(BaseModel):
    strategy_id: str
    candles_symbol: str = "RELIANCE"
    lookback: int = 90


class TickRequest(BaseModel):
    lookahead_days: int = 30


# ---------- Endpoints ----------

@router.post("/deliberate")
async def deliberate(body: DeliberateRequest, authorization: Optional[str] = Header(default=None)):
    """SKILL: trading.deliberate — run full Hermes workflow for a symbol."""
    _auth(authorization)
    if not ops_state.can_open_orders():
        return {"status": "PAUSED_OR_HALTED", "detail": ops_state.get().halt_reason}
    result = await _HERMES.execute_supervisory_workflow(
        symbol=body.symbol,
        portfolio_value=body.portfolio_value,
        conduct_web_research=body.conduct_web_research,
    )
    return {"status": "OK", "deliberation": result}


@router.post("/place_or_hold")
async def place_or_hold(body: PlaceOrderRequest, authorization: Optional[str] = Header(default=None)):
    """SKILL: trading.place_or_hold — route an order through the Portfolio Manager."""
    _auth(authorization)
    summary = _ACCOUNT.get_portfolio_summary()
    trader_proposal = {
        "symbol": body.symbol,
        "action": body.action,
        "entry_price": body.entry_price,
        "stop_loss": body.stop_loss or body.entry_price * 0.97,
        "target_1": body.target or body.entry_price * 1.06,
        "target_2": (body.target or body.entry_price * 1.06) * 1.05,
        "suggested_allocation_pct": min(15.0, (body.quantity * body.entry_price / max(1.0, summary["total_portfolio_value"])) * 100.0),
    }
    risk_evaluation = {
        "approved": True,
        "max_approved_shares": body.quantity,
        "summary": "External risk check assumed by caller.",
    }
    decision = await _PM.authorize_trade(
        symbol=body.symbol,
        trader_proposal=trader_proposal,
        risk_evaluation=risk_evaluation,
        current_portfolio={
            "cash": summary["cash_balance"],
            "total_value": summary["total_portfolio_value"],
            "positions": summary["positions"],
        },
    )
    if not decision.get("trade_executed"):
        return {"status": decision["status"], "reason": decision.get("reason", ""), "decision": decision}

    order = decision["order_details"]
    fill = _ACCOUNT.place_order(
        symbol=order["symbol"],
        action=order["action"],
        quantity=int(order["quantity"]),
        market_price=float(order["entry_price"]),
        stop_loss=order.get("stop_loss"),
        target=order.get("target_1"),
    )
    return {"status": "OK", "decision": decision, "fill": fill}


@router.post("/tick_and_reflect")
async def tick_and_reflect(body: TickRequest, authorization: Optional[str] = Header(default=None)):
    """SKILL: trading.tick_and_reflect — advance N bars, fire stops/targets, close positions."""
    _auth(authorization)
    exits_recorded: List[Dict[str, Any]] = []
    for _ in range(max(1, min(body.lookahead_days, 60))):
        bar: Dict[str, Dict[str, float]] = {}
        for symbol in list(_ACCOUNT.positions.keys()):
            try:
                candles = await _PROVIDER.get_history(symbol, timeframe="1D", limit=2)
            except Exception:
                continue
            if candles:
                c = candles[-1]
                bar[symbol] = {"high": float(c.high), "low": float(c.low), "close": float(c.close)}
        if not bar:
            break
        exits = _ACCOUNT.tick(bar)
        exits_recorded.extend(exits)
        if not _ACCOUNT.positions:
            break
    return {"status": "OK", "exits_recorded": exits_recorded, "positions_remaining": len(_ACCOUNT.positions)}


@router.get("/paper_status")
async def paper_status(digest: bool = Query(False), authorization: Optional[str] = Header(default=None)):
    """SKILL: trading.paper_status — account snapshot; optional formatted digest."""
    _auth(authorization)
    summary = _ACCOUNT.get_portfolio_summary()
    payload: Dict[str, Any] = {"status": "OK", "summary": summary, "ops": {
        "paused": ops_state.get().paused,
        "halted": ops_state.get().halted,
        "halt_reason": ops_state.get().halt_reason,
        "llm_calls_today": ops_state.get().llm_calls_today,
    }}
    if digest:
        payload["digest_text"] = format_end_of_day(summary)
    return payload


@router.post("/evolve_strategy")
async def evolve_strategy(body: EvolveRequest, authorization: Optional[str] = Header(default=None)):
    """SKILL: trading.evolve_strategy — critique a strategy and mutate (re-backtested inside)."""
    _auth(authorization)
    # For now: only allow evolution of a hardcoded reference strategy. A real UI would
    # load StrategyModel from DB by id.
    from services.strategy_dsl.schema import (
        StrategyDefinition, RuleGroup, ConditionRule,
        RiskManagementConfig, PositionSizingConfig,
    )
    strat = StrategyDefinition(
        strategy_id=body.strategy_id or "STRAT_MOMENTUM_V1",
        name="Reference Momentum",
        description="Reference strategy exposed to the evolve skill.",
        version="1.0.0",
        asset_universe=[body.candles_symbol],
        timeframe="1D",
        entry_rules=RuleGroup(logical_operator="AND", conditions=[
            ConditionRule(feature="rsi_14", operator=">", threshold=52.0)
        ]),
        exit_rules=RuleGroup(logical_operator="OR", conditions=[
            ConditionRule(feature="rsi_14", operator=">", threshold=78.0)
        ]),
        risk_management=RiskManagementConfig(stop_loss_pct=3.5, take_profit_pct=7.5),
        position_sizing=PositionSizingConfig(sizing_type="FIXED_RISK_PCT", risk_per_trade_pct=2.0),
    )
    candles = await _PROVIDER.get_history(body.candles_symbol, timeframe="1D", limit=body.lookback)
    bt = BacktestEngine().run_backtest(strat, candles=candles)
    res = _EVOLUTION.critique_and_evolve(strat, bt, candles=candles)
    # StrategyDefinition serializes via pydantic
    res["mutated_strategy"] = res["mutated_strategy"].model_dump()
    return {"status": "OK", "evolution": res, "parent_backtest": bt.get("metrics", {})}


@router.get("/tournament")
async def tournament(asset: str = "RELIANCE", authorization: Optional[str] = Header(default=None)):
    """SKILL: trading.tournament — return the current leaderboard for an asset."""
    _auth(authorization)
    from services.strategy_dsl.schema import (
        StrategyDefinition, RuleGroup, ConditionRule,
        RiskManagementConfig, PositionSizingConfig,
    )
    strat_a = StrategyDefinition(
        strategy_id="STRAT_MOMENTUM_V1", name="Large-Cap Momentum V1",
        description="Momentum reference", version="1.0.0",
        asset_universe=[asset], timeframe="1D",
        entry_rules=RuleGroup(logical_operator="AND",
                              conditions=[ConditionRule(feature="rsi_14", operator=">", threshold=52.0)]),
        exit_rules=RuleGroup(logical_operator="OR",
                             conditions=[ConditionRule(feature="rsi_14", operator=">", threshold=78.0)]),
        risk_management=RiskManagementConfig(stop_loss_pct=3.5, take_profit_pct=7.5),
        position_sizing=PositionSizingConfig(sizing_type="FIXED_RISK_PCT", risk_per_trade_pct=2.0),
    )
    strat_b = StrategyDefinition(
        strategy_id="STRAT_MEAN_REV_V1", name="Mean Reversion Dip Buyer V1",
        description="Mean reversion reference", version="1.0.0",
        asset_universe=[asset], timeframe="1D",
        entry_rules=RuleGroup(logical_operator="AND",
                              conditions=[ConditionRule(feature="rsi_14", operator="<", threshold=40.0)]),
        exit_rules=RuleGroup(logical_operator="OR",
                             conditions=[ConditionRule(feature="rsi_14", operator=">", threshold=60.0)]),
        risk_management=RiskManagementConfig(stop_loss_pct=4.0, take_profit_pct=8.0),
        position_sizing=PositionSizingConfig(sizing_type="FIXED_RISK_PCT", risk_per_trade_pct=2.0),
    )
    result = await _TOURNAMENT.run_tournament(strategies=[strat_a, strat_b], asset=asset)
    return {"status": "OK", "leaderboard": result.get("leaderboard", [])}


@router.get("/ops/health")
async def health(authorization: Optional[str] = Header(default=None)):
    """SKILL: trading.health — governance & runtime state."""
    _auth(authorization)
    cfg = ops_config.load()
    st = ops_state.get()
    return {
        "status": "OK",
        "runtime": {
            "paused": st.paused,
            "halted": st.halted,
            "halt_reason": st.halt_reason,
            "last_tick_ok": st.last_tick_ok,
            "last_error": st.last_error,
        },
        "budget": {
            "llm_calls_today": st.llm_calls_today,
            "llm_calls_hour": st.llm_calls_hour,
            "max_llm_calls_per_day": cfg.max_llm_calls_per_day,
            "errors_this_hour": st.errors_this_hour,
        },
        "positions_open": len(_ACCOUNT.positions),
        "quarantined": st.quarantined,
    }


@router.post("/ops/pause")
async def ops_pause(reason: str = "", authorization: Optional[str] = Header(default=None)):
    _auth(authorization)
    ops_state.pause(reason)
    return {"status": "PAUSED", "reason": reason}


@router.post("/ops/resume")
async def ops_resume(authorization: Optional[str] = Header(default=None)):
    _auth(authorization)
    ops_state.resume()
    return {"status": "RESUMED"}


@router.post("/ops/halt")
async def ops_halt(reason: str, authorization: Optional[str] = Header(default=None)):
    _auth(authorization)
    ops_state.halt(reason)
    return {"status": "HALTED", "reason": reason}
