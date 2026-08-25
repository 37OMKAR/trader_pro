"""
Market AI — Market Data Provider Abstraction
Defines the strict abstract base class for all market data ingestion.
All market data consumption throughout the platform MUST pass through this interface.
"""

from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Optional, Dict
from packages.shared_types.market_types import (
    Quote,
    IndexQuote,
    Candle,
    MarketBreadth,
    FiiDiiActivity,
    SectorPerformance,
    SymbolInfo,
)


class MarketDataProvider(ABC):
    """Abstract interface for all Indian market data providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the data provider (e.g. 'DevelopmentSimulator', 'YahooFinance', 'KiteConnect')."""
        pass

    @abstractmethod
    async def get_quote(self, symbol: str) -> Quote:
        """Fetch current live or latest quote for a given equity or index symbol."""
        pass

    @abstractmethod
    async def get_index_quotes(self) -> List[IndexQuote]:
        """Fetch quotes for key Indian indices (NIFTY 50, SENSEX, BANK NIFTY, FINNIFTY, INDIA VIX)."""
        pass

    @abstractmethod
    async def get_history(
        self,
        symbol: str,
        timeframe: str = "1D",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Candle]:
        """Fetch historical OHLCV candlestick series for an instrument."""
        pass

    @abstractmethod
    async def get_market_breadth(self) -> MarketBreadth:
        """Fetch current market advance-decline statistics."""
        pass

    @abstractmethod
    async def get_fii_dii_activity(self, target_date: Optional[date] = None) -> FiiDiiActivity:
        """Fetch institutional cash market investment flows in INR Crores."""
        pass

    @abstractmethod
    async def get_sector_performance(self) -> List[SectorPerformance]:
        """Fetch real-time performance of key NIFTY sectors."""
        pass

    @abstractmethod
    async def get_symbols(self, query: Optional[str] = None, limit: int = 50) -> List[SymbolInfo]:
        """Search or list symbols in the active trading universe."""
        pass
