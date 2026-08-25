"""
Market AI — Shared Domain Models and Schemas
Strict typed representations for Indian Market instruments, quotes, candles,
indices, market breadth, FII/DII activity, calendar sessions, and regimes.
"""

from datetime import datetime, date, time
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Exchange(str, Enum):
    NSE = "NSE"
    BSE = "BSE"
    MCX = "MCX"


class InstrumentType(str, Enum):
    EQUITY = "EQUITY"
    INDEX = "INDEX"
    FUTURES = "FUTURES"
    OPTIONS = "OPTIONS"


class OptionType(str, Enum):
    CE = "CE"  # Call European
    PE = "PE"  # Put European


class MarketSessionStatus(str, Enum):
    CLOSED = "CLOSED"
    PRE_OPEN = "PRE_OPEN"
    OPEN = "OPEN"
    SPECIAL_SESSION = "SPECIAL_SESSION"
    POST_CLOSE = "POST_CLOSE"
    HOLIDAY = "HOLIDAY"
    WEEKEND = "WEEKEND"


class MarketRegime(str, Enum):
    BULL = "BULL"
    BEAR = "BEAR"
    RANGE = "RANGE"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    RISK_ON = "RISK_ON"
    RISK_OFF = "RISK_OFF"
    TRANSITION = "TRANSITION"


class SymbolInfo(BaseModel):
    exchange: Exchange = Exchange.NSE
    symbol: str  # e.g., "RELIANCE", "NIFTY 50"
    isin: Optional[str] = None
    company_name: str
    instrument_type: InstrumentType = InstrumentType.EQUITY
    series: str = "EQ"
    sector: Optional[str] = None
    industry: Optional[str] = None
    lot_size: int = 1
    tick_size: float = 0.05
    active: bool = True


class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    open_interest: Optional[int] = None
    turnover: Optional[float] = None


class Quote(BaseModel):
    symbol: str
    exchange: Exchange = Exchange.NSE
    company_name: Optional[str] = None
    last_price: float
    change: float
    percent_change: float
    open: float
    high: float
    low: float
    previous_close: float
    volume: int
    value: Optional[float] = None  # Turnover in Crores / INR
    vwap: Optional[float] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    provider: str = "DevelopmentMarketDataProvider"


class IndexQuote(BaseModel):
    symbol: str  # e.g., "NIFTY 50", "NIFTY BANK", "SENSEX", "FINNIFTY", "INDIA VIX"
    name: str
    current_value: float
    change: float
    percent_change: float
    open: float
    high: float
    low: float
    previous_close: float
    advances: Optional[int] = None
    declines: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MarketBreadth(BaseModel):
    advances: int
    declines: int
    unchanged: int
    advance_decline_ratio: float
    highs_52w: int
    lows_52w: int
    upper_circuits: int
    lower_circuits: int
    total_traded_stocks: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class FiiDiiActivity(BaseModel):
    date: date
    fii_buy_gross: float  # In INR Crores
    fii_sell_gross: float
    fii_net: float
    dii_buy_gross: float
    dii_sell_gross: float
    dii_net: float
    total_institutional_net: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SectorPerformance(BaseModel):
    sector_name: str  # e.g., "NIFTY IT", "NIFTY BANK", "NIFTY AUTO", "NIFTY PHARMA"
    symbol: str
    current_value: float
    percent_change: float
    change: float
    top_contributor: Optional[str] = None
    weight_pct: Optional[float] = None


class MarketRegimeState(BaseModel):
    regime: MarketRegime = MarketRegime.BULL
    probability: float = Field(ge=0.0, le=1.0, default=0.75)
    confidence: float = Field(ge=0.0, le=1.0, default=0.72)
    drivers: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LiveTickerMessage(BaseModel):
    event_type: str = "TICK"
    symbol: str
    price: float
    change: float
    percent_change: float
    volume: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
