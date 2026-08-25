"""
Market AI — Option Chain & Derivatives REST Endpoints
Provides live option chain strike ladders, PCR, Max Pain, and Greeks.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Query, HTTPException
from packages.derivatives_engine.option_chain import OptionChainEngine
from packages.market_data.development_provider import DevelopmentMarketDataProvider

router = APIRouter(prefix="/derivatives", tags=["Derivatives & Options"])

option_chain_engine = OptionChainEngine()
market_provider = DevelopmentMarketDataProvider()


@router.get("/option-chain/{symbol}")
async def get_option_chain(
    symbol: str,
    num_strikes: int = Query(15, ge=5, le=31, description="Number of strikes to display"),
):
    """Fetch live option chain with Greeks and OI for NIFTY, BANK NIFTY, or any F&O stock."""
    symbol_upper = symbol.upper()
    try:
        quote = await market_provider.get_quote(symbol_upper)
        spot_price = quote.last_price
    except Exception:
        spot_price = 24500.0 if "NIFTY" in symbol_upper else 1500.0

    return option_chain_engine.generate_option_chain(
        symbol=symbol_upper,
        spot_price=spot_price,
        num_strikes=num_strikes,
    )


@router.get("/fno-universe")
async def get_fno_universe():
    """Returns list of active Indian F&O underlying assets."""
    return [
        {"symbol": "NIFTY 50", "name": "NIFTY 50 Index", "type": "INDEX", "lot": 25},
        {"symbol": "BANKNIFTY", "name": "NIFTY Bank Index", "type": "INDEX", "lot": 15},
        {"symbol": "FINNIFTY", "name": "NIFTY Financial Services", "type": "INDEX", "lot": 25},
        {"symbol": "RELIANCE", "name": "Reliance Industries Ltd", "type": "STOCK", "lot": 250},
        {"symbol": "TCS", "name": "Tata Consultancy Services", "type": "STOCK", "lot": 175},
        {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "type": "STOCK", "lot": 550},
        {"symbol": "INFY", "name": "Infosys Ltd", "type": "STOCK", "lot": 400},
        {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "type": "STOCK", "lot": 700},
        {"symbol": "SBIN", "name": "State Bank of India", "type": "STOCK", "lot": 750},
        {"symbol": "TATAMOTORS", "name": "Tata Motors Ltd", "type": "STOCK", "lot": 1425},
    ]
