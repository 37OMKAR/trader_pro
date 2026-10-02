"""
Market AI — Production-Ready Paper Trading REST Endpoints
Manages dummy money virtual accounts, live NSE/BSE order matching, database persistence, and mark-to-market valuations.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Query, HTTPException, Body, Depends
from services.paper_trading.account import PaperTradingAccount
from packages.market_data.yahoo_provider import YahooFinanceMarketDataProvider
from packages.market_data.development_provider import DevelopmentMarketDataProvider
from apps.api.app.db.session import async_session_factory
from apps.api.app.db.models import PaperAccountModel, PaperTradeModel, PaperPositionModel
from apps.api.app.core.security import require_api_key, caller_id
from sqlalchemy import select

router = APIRouter(prefix="/paper", tags=["Paper Trading"])

# Per-caller paper accounts, keyed by X-User-Id (default "public").
# Falls back to the legacy singleton name for backwards compatibility.
_ACCOUNTS: Dict[str, PaperTradingAccount] = {}
_DEFAULT_CAPITAL = 1_000_000.0


def _get_account(user_id: str) -> PaperTradingAccount:
    acc = _ACCOUNTS.get(user_id)
    if acc is None:
        acc = PaperTradingAccount(
            account_id=f"HERMES_ALPHA_{user_id.upper()}",
            name=f"Hermes Alpha Fund — {user_id}",
            initial_capital=_DEFAULT_CAPITAL,
        )
        _ACCOUNTS[user_id] = acc
    return acc


# Legacy alias — any remaining importer still works.
master_account = _get_account("public")
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
async def get_paper_account_summary(user: str = Depends(caller_id)):
    """Returns live account balance, margin, positions, and mark-to-market P&L with database sync."""
    account = _get_account(user)
    quotes_map: Dict[str, float] = {}
    for sym in account.positions.keys():
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

    summary = account.get_portfolio_summary(current_quotes=quotes_map)

    # Persist live state to DB
    try:
        async with async_session_factory() as session:
            existing = await session.scalar(select(PaperAccountModel).where(PaperAccountModel.account_id == account.account_id))
            if existing:
                existing.current_cash = summary["cash_balance"]
                existing.portfolio_value = summary["total_portfolio_value"]
                existing.realized_pnl = summary["realized_pnl"]
                existing.unrealized_pnl = summary["unrealized_pnl"]
            else:
                acc_model = PaperAccountModel(
                    account_id=account.account_id,
                    name=account.name,
                    initial_balance=account.initial_capital,
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


@router.post("/orders/place", dependencies=[Depends(require_api_key)])
async def place_paper_order(req: OrderPlacementRequest, user: str = Depends(caller_id)):
    """Submits and matches a simulated paper trading order against real live market feeds and commits to DB."""
    account = _get_account(user)
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

    result = account.place_order(
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
                account_id=account.account_id,
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


class AccountResetRequest(BaseModel):
    initial_balance: float = 1_000_000.0


@router.post("/account/reset", dependencies=[Depends(require_api_key)])
async def reset_paper_account(
    req: Optional[AccountResetRequest] = Body(None),
    capital: float = Query(1_000_000.0, ge=10_000.0),
    user: str = Depends(caller_id),
):
    """Reset the caller's paper account to fresh virtual capital.

    Accepts either a JSON body `{initial_balance: ...}` (preferred — matches
    the web client) or a legacy `?capital=` query parameter. Only touches the
    account for the current `X-User-Id` (default "public") — other users are
    unaffected.
    """
    amount = (req.initial_balance if req is not None else capital)
    if amount < 10_000:
        raise HTTPException(status_code=400, detail="initial_balance must be at least 10,000.")
    _ACCOUNTS[user] = PaperTradingAccount(
        account_id=f"HERMES_ALPHA_{user.upper()}",
        name=f"Hermes Alpha Fund — {user}",
        initial_capital=amount,
    )
    global master_account
    if user == "public":
        master_account = _ACCOUNTS[user]
    return {"status": "SUCCESS", "message": f"Account reset with ₹{amount:,.2f} virtual capital."}
