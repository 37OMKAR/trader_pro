"""
Market AI — Paper Trading REST Endpoints
Manages dummy money virtual accounts, order placement, positions, and live mark-to-market valuations.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Query, HTTPException, Body
from services.paper_trading.account import PaperTradingAccount
from packages.market_data.development_provider import DevelopmentMarketDataProvider

router = APIRouter(prefix="/paper", tags=["Paper Trading"])

# Singleton master paper account (₹10,00,000 virtual capital)
master_account = PaperTradingAccount(
    account_id="MASTER_PAPER_V1",
    name="Market AI Institutional Virtual Portfolio",
    initial_capital=1_000_000.0,
)
market_provider = DevelopmentMarketDataProvider()


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
    """Returns live account balance, margin, positions, and mark-to-market P&L."""
    quotes_map: Dict[str, float] = {}
    for sym in master_account.positions.keys():
        try:
            q = await market_provider.get_quote(sym)
            quotes_map[sym] = q.last_price
        except Exception:
            pass

    return master_account.get_portfolio_summary(current_quotes=quotes_map)


@router.post("/orders/place")
async def place_paper_order(req: OrderPlacementRequest):
    """Submits and matches a simulated paper trading order."""
    sym = req.symbol.upper().strip()
    try:
        quote = await market_provider.get_quote(sym)
        current_market_price = quote.last_price
    except Exception:
        raise HTTPException(status_code=404, detail=f"Market price for {sym} unavailable.")

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

    return result


@router.post("/account/reset")
async def reset_paper_account(capital: float = Query(1_000_000.0, ge=10000.0)):
    """Resets paper account to fresh virtual capital."""
    global master_account
    master_account = PaperTradingAccount(
        account_id="MASTER_PAPER_V1",
        name="Market AI Institutional Virtual Portfolio",
        initial_capital=capital,
    )
    return {"status": "SUCCESS", "message": f"Account reset with ₹{capital:,.2f} virtual capital."}
