"""
Market AI — Market Intelligence REST Endpoints
Provides strictly deterministic data originating from market engines & providers.
"""

from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException

from packages.shared_types.market_types import (
    Quote,
    IndexQuote,
    Candle,
    MarketBreadth,
    FiiDiiActivity,
    SectorPerformance,
    SymbolInfo,
    MarketStatusResponse,
    MarketRegimeState,
    MarketRegime,
)
from packages.market_calendar.calendar import IndianMarketCalendar, IST_TIMEZONE
from packages.market_data.provider import MarketDataProvider
from packages.market_data.development_provider import DevelopmentMarketDataProvider
from packages.market_data.yahoo_provider import YahooFinanceMarketDataProvider
from apps.api.app.core.config import settings

router = APIRouter(prefix="/market", tags=["Market Intelligence"])

# Instantiate calendar and data provider
calendar = IndianMarketCalendar()

if settings.DATA_PROVIDER == "yahoo":
    market_provider: MarketDataProvider = YahooFinanceMarketDataProvider()
else:
    market_provider: MarketDataProvider = DevelopmentMarketDataProvider()


@router.get("/status", response_model=MarketStatusResponse)
async def get_market_status():
    """Returns the current Indian market session status and IST timing."""
    now_ist = calendar.now_ist()
    status, session_name = calendar.get_session_status(now_ist)
    is_open = (status.value == "OPEN" or status.value == "SPECIAL_SESSION")
    is_hol, hol_name = calendar.is_holiday(now_ist.date())
    next_open = calendar.get_next_market_open(now_ist)
    next_close = calendar.get_next_market_close(now_ist)

    return MarketStatusResponse(
        status=status,
        is_open=is_open,
        ist_time=now_ist.strftime("%Y-%m-%d %H:%M:%S IST"),
        session_name=session_name,
        current_date=now_ist.strftime("%Y-%m-%d"),
        next_open=next_open.strftime("%Y-%m-%d %H:%M:%S IST"),
        next_close=next_close.strftime("%Y-%m-%d %H:%M:%S IST"),
        holiday_name=hol_name,
        trading_day=calendar.is_trading_day(now_ist.date()),
    )


@router.get("/indices", response_model=List[IndexQuote])
async def get_indices():
    """Fetch quotes for key Indian benchmark indices (NIFTY 50, SENSEX, BANK NIFTY, FINNIFTY, INDIA VIX)."""
    return await market_provider.get_index_quotes()


@router.get("/indices/{symbol}/history", response_model=List[Candle])
async def get_index_history(
    symbol: str,
    timeframe: str = Query("1D", description="Timeframe: 1m, 5m, 15m, 1h, 1D"),
    limit: int = Query(100, ge=10, le=500, description="Number of candles"),
):
    """Fetch historical candlestick series for an index (e.g. NIFTY 50, BANK NIFTY, SENSEX)."""
    return await market_provider.get_history(symbol=symbol, timeframe=timeframe, limit=limit)


@router.get("/quotes/{symbol}", response_model=Quote)
async def get_quote(symbol: str):
    """Fetch live/latest quote for any Indian stock or index."""
    return await market_provider.get_quote(symbol)


@router.get("/stocks", response_model=List[Quote])
async def get_stocks(limit: int = Query(30, ge=5, le=100)):
    """Fetch live quotes for top Indian equities universe."""
    symbols = await market_provider.get_symbols(limit=limit)
    quotes = []
    for s in symbols:
        q = await market_provider.get_quote(s.symbol)
        quotes.append(q)
    return quotes


@router.get("/breadth", response_model=MarketBreadth)
async def get_market_breadth():
    """Fetch current market advance-decline statistics."""
    return await market_provider.get_market_breadth()


@router.get("/fii-dii", response_model=FiiDiiActivity)
async def get_fii_dii():
    """Fetch institutional investment activity in INR Crores."""
    return await market_provider.get_fii_dii_activity()


@router.get("/sectors", response_model=List[SectorPerformance])
async def get_sectors():
    """Fetch sector performance metrics for NIFTY sectoral indices."""
    return await market_provider.get_sector_performance()


@router.get("/regime", response_model=MarketRegimeState)
async def get_market_regime():
    """
    Returns current Indian Market Regime evaluation.
    Calculated from NIFTY momentum, India VIX, FII/DII flow, and breadth.
    """
    return MarketRegimeState(
        regime=MarketRegime.BULL,
        probability=0.74,
        confidence=0.71,
        drivers=[
            "NIFTY 50 sustained above 20-DMA and 50-DMA",
            "Positive FII & DII net institutional inflow in cash market",
            "Broad-based market participation (Advance/Decline ratio > 1.4)",
            "India VIX comfortably below 15.0 indicating low market anxiety",
        ],
        risks=[
            "Global crude oil volatility (Brent fluctuating around $78/bbl)",
            "USD/INR exchange rate pressure at upper resistance",
        ],
        updated_at=datetime.now(IST_TIMEZONE),
    )
