"""
Market AI — Strategy DSL & Backtesting REST Endpoints
Allows creating, backtesting, and generating strategies via Natural Language & DSL.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Query, HTTPException, Body
from services.strategy_dsl.schema import StrategyDefinition, RuleGroup, ConditionRule, RiskManagementConfig, PositionSizingConfig
from services.backtest_engine.engine import BacktestEngine
from packages.market_data.development_provider import DevelopmentMarketDataProvider

router = APIRouter(prefix="/strategies", tags=["Strategy Lab & Backtester"])

backtest_engine = BacktestEngine()
market_provider = DevelopmentMarketDataProvider()


class NLStrategyRequest(BaseModel):
    prompt: str


@router.get("/templates")
async def get_strategy_templates():
    """Returns curated institutional quantitative strategy templates."""
    return [
        {
            "strategy_id": "RSI_PULLBACK_EMA50",
            "name": "RSI Trend Pullback (Golden Stack)",
            "description": "Buys oversold RSI (<40) dips while asset is in strong long-term uptrend above 50-DMA.",
            "category": "MOMENTUM_PULLBACK",
            "timeframe": "1D",
            "entry_rules": {
                "logical_operator": "AND",
                "conditions": [
                    {"feature": "rsi_14", "operator": "<", "threshold": 42.0},
                    {"feature": "close", "operator": ">", "threshold": "sma_50"},
                ],
            },
            "risk_management": {"stop_loss_pct": 2.5, "take_profit_pct": 6.0},
        },
        {
            "strategy_id": "VOL_BREAKOUT_NIFTY_ALPHA",
            "name": "Volume Z-Score & Relative Alpha Breakout",
            "description": "Enters on high volume surge (>1.5 z-score) with strong alpha outperformance vs NIFTY 50.",
            "category": "BREAKOUT",
            "timeframe": "1D",
            "entry_rules": {
                "logical_operator": "AND",
                "conditions": [
                    {"feature": "volume_zscore", "operator": ">", "threshold": 1.2},
                    {"feature": "relative_strength_nifty", "operator": ">", "threshold": 55.0},
                    {"feature": "close", "operator": ">", "threshold": "sma_20"},
                ],
            },
            "risk_management": {"stop_loss_pct": 3.0, "take_profit_pct": 8.0},
        },
        {
            "strategy_id": "BOLLINGER_SQUEEZE_EXPANSION",
            "name": "Bollinger Band Squeeze Reversal",
            "description": "Enters on mean-reversion touch of lower Bollinger Band in healthy trending markets.",
            "category": "MEAN_REVERSION",
            "timeframe": "1D",
            "entry_rules": {
                "logical_operator": "AND",
                "conditions": [
                    {"feature": "close", "operator": "<=", "threshold": "bollinger_lower"},
                    {"feature": "rsi_14", "operator": ">=", "threshold": 30.0},
                ],
            },
            "risk_management": {"stop_loss_pct": 2.0, "take_profit_pct": 5.0},
        },
    ]


@router.post("/generate-from-prompt")
async def generate_strategy_from_prompt(req: NLStrategyRequest):
    """Translates natural language strategy ideas into strict Strategy DSL."""
    p = req.prompt.lower()

    if "breakout" in p or "volume" in p:
        return StrategyDefinition(
            strategy_id=f"NL_VOL_BREAKOUT",
            name="AI Generated: High Volume Breakout",
            description=req.prompt,
            entry_rules=RuleGroup(
                logical_operator="AND",
                conditions=[
                    ConditionRule(feature="volume_zscore", operator=">", threshold=1.0),
                    ConditionRule(feature="close", operator=">", threshold="sma_20"),
                ],
            ),
            risk_management=RiskManagementConfig(stop_loss_pct=2.5, take_profit_pct=7.0),
        )
    elif "rsi" in p or "oversold" in p:
        return StrategyDefinition(
            strategy_id=f"NL_RSI_OVERSOLD",
            name="AI Generated: RSI Oversold Reversal",
            description=req.prompt,
            entry_rules=RuleGroup(
                logical_operator="AND",
                conditions=[
                    ConditionRule(feature="rsi_14", operator="<", threshold=35.0),
                    ConditionRule(feature="close", operator=">", threshold="sma_50"),
                ],
            ),
            risk_management=RiskManagementConfig(stop_loss_pct=2.0, take_profit_pct=6.0),
        )
    else:
        return StrategyDefinition(
            strategy_id=f"NL_CUSTOM_TREND",
            name="AI Generated: Multi-Factor Trend Momentum",
            description=req.prompt,
            entry_rules=RuleGroup(
                logical_operator="AND",
                conditions=[
                    ConditionRule(feature="close", operator=">", threshold="sma_20"),
                    ConditionRule(feature="relative_strength_nifty", operator=">", threshold=52.0),
                ],
            ),
            risk_management=RiskManagementConfig(stop_loss_pct=3.0, take_profit_pct=7.5),
        )


@router.post("/backtest")
async def execute_backtest(
    body: Dict[str, Any] = Body(...),
    symbol: str = Query("RELIANCE", description="Asset to test on"),
    initial_capital: float = Query(1_000_000.0, description="Initial capital (query — legacy clients)"),
):
    """Executes a backtest on historical data with the given strategy DSL.

    Accepts either shape:

    - **Modern (web client):** `{"strategy": {...}, "symbol": "RELIANCE", "capital": 1000000}`
    - **Legacy:** full `StrategyDefinition` JSON in the body + `?symbol=...&initial_capital=...`
      query parameters.

    Missing strategy fields are filled with sensible defaults so the Strategy Lab UI
    does not need to pass the entire schema just to kick off a test.
    """
    if isinstance(body, dict) and "strategy" in body and isinstance(body["strategy"], dict):
        raw = dict(body["strategy"])
        sym = (body.get("symbol") or symbol or "RELIANCE").upper()
        capital = float(body.get("capital", body.get("initial_capital", initial_capital)))
    else:
        raw = dict(body or {})
        sym = symbol.upper()
        capital = float(initial_capital)

    raw.setdefault("strategy_id", "ADHOC_WEB_BACKTEST")
    raw.setdefault("name", "Ad-hoc web backtest")
    raw.setdefault("description", "Backtest requested from the web dashboard")
    raw.setdefault("timeframe", "1D")
    if "entry_rules" not in raw:
        raw["entry_rules"] = {
            "logical_operator": "AND",
            "conditions": [{"feature": "close", "operator": ">", "threshold": "sma_20"}],
        }
    raw.setdefault("risk_management", {"stop_loss_pct": 2.5, "take_profit_pct": 6.0})
    try:
        strategy = StrategyDefinition(**raw)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid strategy: {exc}")

    candles = await market_provider.get_history(sym, timeframe=strategy.timeframe, limit=80)
    return backtest_engine.run_backtest(
        strategy=strategy,
        candles=candles,
        initial_capital=capital,
    )
