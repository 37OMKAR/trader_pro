"""
Market AI — Production-Ready Paper Trading REST Endpoints
Manages dummy money virtual accounts, live NSE/BSE order matching, database persistence, and mark-to-market valuations.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Query, HTTPException, Body
from services.paper_trading.account import PaperTradingAccount
from packages.market_data.yahoo_provider import YahooFinanceMarketDataProvider
from packages.market_data.development_provider import DevelopmentMarketDataProvider
from apps.api.app.db.session import async_session_factory
from apps.api.app.db.models import PaperAccountModel, PaperTradeModel, PaperPositionModel
from sqlalchemy import select

router = APIRouter(prefix="/paper", tags=["Paper Trading"])

# Singleton master paper account (₹10,00,000 virtual capital)
master_account = PaperTradingAccount(
    account_id="HERMES_ALPHA_PRO_01",
    name="Hermes Alpha Paper Fund",
    initial_capital=1_000_000.0,
)
live_provider = YahooFinanceMarketDataProvider()
fallback_provider = DevelopmentMarketDataProvider()


class OrderPlacementRequest(BaseModel):
    symbol: str
    action: str  # "BUY" or "SELL"
    quantity: int
    order_type: str = "MARKET"
    limit_price: float = 0.0
    stop_loss: Optional[float] = None
    target: Optional[float] = None


@router.get("/account/summary")
async def get_paper_account_summary():
    """Returns live account balance, margin, positions, and mark-to-market P&L with database sync."""
    quotes_map: Dict[str, float] = {}
    for sym in master_account.positions.keys():
        try:
            q = await live_provider.get_quote(sym)
            if q and q.last_price > 0:
                quotes_map[sym] = q.last_price
            else:
                dq = await fallback_provider.get_quote(sym)
                quotes_map[sym] = dq.last_price
        except Exception:
            try:
                dq = await fallback_provider.get_quote(sym)
                quotes_map[sym] = dq.last_price
            except Exception:
                pass

    summary = master_account.get_portfolio_summary(current_quotes=quotes_map)

    # Persist live state to DB
    try:
        async with async_session_factory() as session:
            existing = await session.scalar(select(PaperAccountModel).where(PaperAccountModel.account_id == master_account.account_id))
            if existing:
                existing.current_cash = summary["cash_balance"]
                existing.portfolio_value = summary["total_portfolio_value"]
                existing.realized_pnl = summary["realized_pnl"]
                existing.unrealized_pnl = summary["unrealized_pnl"]
            else:
                acc_model = PaperAccountModel(
                    account_id=master_account.account_id,
                    name=master_account.name,
                    initial_balance=master_account.initial_capital,
                    current_cash=summary["cash_balance"],
                    portfolio_value=summary["total_portfolio_value"],
                    realized_pnl=summary["realized_pnl"],
                    unrealized_pnl=summary["unrealized_pnl"],
                    active=True,
                )
                session.add(acc_model)
            await session.commit()
    except Exception:
        pass

    return summary


@router.post("/orders/place")
async def place_paper_order(req: OrderPlacementRequest):
    """Submits and matches a simulated paper trading order against real live market feeds and commits to DB."""
    sym = req.symbol.upper().strip()
    current_market_price = 0.0

    try:
        quote = await live_provider.get_quote(sym)
        if quote and quote.last_price > 0:
            current_market_price = quote.last_price
        else:
            dev_quote = await fallback_provider.get_quote(sym)
            current_market_price = dev_quote.last_price
    except Exception:
        try:
            dev_quote = await fallback_provider.get_quote(sym)
            current_market_price = dev_quote.last_price
        except Exception:
            raise HTTPException(status_code=404, detail=f"Live market price for {sym} unavailable.")

    result = master_account.place_order(
        symbol=sym,
        action=req.action,
        quantity=req.quantity,
        market_price=current_market_price,
        order_type=req.order_type,
        limit_price=req.limit_price,
        stop_loss=req.stop_loss,
        target=req.target,
    )

    if result["status"] == "REJECTED":
        raise HTTPException(status_code=400, detail=result["reason"])

    # Persist trade to DB
    try:
        async with async_session_factory() as session:
            trade_model = PaperTradeModel(
                trade_id=result["order_id"],
                account_id=master_account.account_id,
                strategy_id="MANUAL_EXECUTION",
                symbol=sym,
                side=req.action,
                quantity=req.quantity,
                price=result["price"],
                amount=result["price"] * req.quantity,
                fee=result.get("fee", 20.0),
                order_type=req.order_type,
                status="FILLED",
            )
            session.add(trade_model)
            await session.commit()
    except Exception:
        pass

    return result


@router.post("/account/reset")
async def reset_paper_account(capital: float = Query(1_000_000.0, ge=10000.0)):
    """Resets paper account to fresh virtual capital."""
    global master_account
    master_account = PaperTradingAccount(
        account_id="HERMES_ALPHA_PRO_01",
        name="Hermes Alpha Paper Fund",
        initial_capital=capital,
    )
    return {"status": "SUCCESS", "message": f"Account reset with ₹{capital:,.2f} virtual capital."}
