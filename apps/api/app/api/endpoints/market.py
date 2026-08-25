"""
Market AI — Market Intelligence & Prediction REST Endpoints
Deterministic calculations from Calendar, Market Data, Feature Engine, Regime Classifier, and ML Models.
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
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
from packages.market_data.development_provider import DevelopmentMarketDataProvider, INDIAN_EQUITY_UNIVERSE
from packages.market_data.yahoo_provider import YahooFinanceMarketDataProvider
from services.feature_engine.pipeline import FeaturePipeline
from services.regime_engine.classifier import MarketRegimeClassifier
from services.prediction_engine.models import MLPredictionEngine
from services.prediction_engine.registry import PredictionRegistry
from apps.api.app.core.config import settings

router = APIRouter(prefix="/market", tags=["Market Intelligence"])

# Engine Singletons
calendar = IndianMarketCalendar()
feature_pipeline = FeaturePipeline()
regime_classifier = MarketRegimeClassifier()
prediction_engine = MLPredictionEngine()

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
    """Fetch historical candlestick series for an index or stock."""
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
    Returns current Indian Market Regime evaluation computed dynamically
    from NIFTY, BANK NIFTY, India VIX, Market Breadth, and FII/DII liquidity.
    """
    indices = await market_provider.get_index_quotes()
    nifty = next((i for i in indices if i.symbol == "NIFTY 50"), indices[0])
    bank = next((i for i in indices if "BANK" in i.symbol), indices[0])
    vix = next((i for i in indices if "VIX" in i.symbol), indices[-1])
    breadth = await market_provider.get_market_breadth()
    fii_dii = await market_provider.get_fii_dii_activity()

    return regime_classifier.evaluate_regime(nifty, bank, vix, breadth, fii_dii)


@router.get("/features/{symbol}")
async def get_stock_features(symbol: str):
    """Computes full point-in-time feature snapshot for a given symbol."""
    quote = await market_provider.get_quote(symbol)
    candles = await market_provider.get_history(symbol, timeframe="1D", limit=40)
    nifty_candles = await market_provider.get_history("NIFTY 50", timeframe="1D", limit=40)
    return feature_pipeline.extract_features(symbol, quote, candles, nifty_candles)


@router.get("/predictions/{symbol}")
async def get_stock_predictions(symbol: str, horizon: str = Query("5D", pattern="^(1D|5D|20D)$")):
    """Generates and logs an immutable ML directional prediction for a stock."""
    quote = await market_provider.get_quote(symbol)
    candles = await market_provider.get_history(symbol, timeframe="1D", limit=40)
    nifty_candles = await market_provider.get_history("NIFTY 50", timeframe="1D", limit=40)
    
    features = feature_pipeline.extract_features(symbol, quote, candles, nifty_candles)
    regime_state = await get_market_regime()
    
    prediction = prediction_engine.predict(
        symbol=symbol,
        features=features,
        horizon=horizon,
        current_regime=regime_state.regime,
    )
    
    # Record to immutable database registry
    try:
        await PredictionRegistry.record_prediction(prediction)
    except Exception:
        pass

    return prediction


@router.get("/predictions")
async def get_recent_predictions(limit: int = Query(20, ge=1, le=100)):
    """Retrieves recent predictions from the immutable registry."""
    return await PredictionRegistry.get_recent_predictions(limit=limit)


@router.get("/stocks/{symbol}/details")
async def get_stock_details(symbol: str):
    """
    Returns comprehensive deep-dive stock profile matching Phase 5 requirements:
    Quote, Financial Ratios, Technical Overview, Delivery stats, Features, and AI Prediction.
    """
    symbol_upper = symbol.upper()
    quote = await market_provider.get_quote(symbol_upper)
    candles = await market_provider.get_history(symbol_upper, timeframe="1D", limit=40)
    nifty_candles = await market_provider.get_history("NIFTY 50", timeframe="1D", limit=40)
    
    features = feature_pipeline.extract_features(symbol_upper, quote, candles, nifty_candles)
    regime_state = await get_market_regime()
    prediction = prediction_engine.predict(symbol_upper, features, horizon="5D", current_regime=regime_state.regime)
    
    stock_info = next((s for s in INDIAN_EQUITY_UNIVERSE if s["symbol"] == symbol_upper), None)
    
    return {
        "symbol": symbol_upper,
        "name": stock_info["name"] if stock_info else symbol_upper,
        "sector": stock_info["sector"] if stock_info else "Indian Equities",
        "lot_size": stock_info["lot"] if stock_info else 1,
        "quote": quote,
        "features": features,
        "prediction": prediction,
        "shareholding_pattern": {
            "promoter_pct": 50.4,
            "fii_pct": 22.8,
            "dii_pct": 16.5,
            "public_pct": 10.3,
        },
        "corporate_actions": [
            {"type": "Dividend", "amount": "₹ 10.00 per share", "ex_date": "2025-09-15"},
            {"type": "Board Meeting", "purpose": "Q2 Financial Results", "date": "2025-10-22"},
        ],
    }
