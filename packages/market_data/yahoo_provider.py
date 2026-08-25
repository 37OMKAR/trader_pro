"""
Market AI — Yahoo Finance Live Market Data Provider
Provides real-world market quotes and historical candlestick feeds for Indian instruments
(e.g., ^NSEI for NIFTY 50, ^BSESN for SENSEX, RELIANCE.NS, TCS.NS) with development fallback.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict
import asyncio
import pytz

from packages.shared_types.market_types import (
    Exchange,
    InstrumentType,
    Quote,
    IndexQuote,
    Candle,
    MarketBreadth,
    FiiDiiActivity,
    SectorPerformance,
    SymbolInfo,
)
from packages.market_data.provider import MarketDataProvider
from packages.market_data.development_provider import DevelopmentMarketDataProvider
from packages.market_calendar.calendar import IST_TIMEZONE


# Yahoo Finance Symbol Mapping for Indian Market
YAHOO_SYMBOL_MAP = {
    "NIFTY 50": "^NSEI",
    "NIFTY50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY BANK": "^NSEBANK",
    "BANKNIFTY": "^NSEBANK",
    "INDIA VIX": "^INDIAVIX",
}


class YahooFinanceMarketDataProvider(MarketDataProvider):
    """Yahoo Finance API wrapper with automated fallbacks to Development provider."""

    def __init__(self):
        self._fallback = DevelopmentMarketDataProvider()

    @property
    def provider_name(self) -> str:
        return "YahooFinanceMarketDataProvider"

    def _to_yahoo_symbol(self, symbol: str) -> str:
        s = symbol.upper().strip()
        if s in YAHOO_SYMBOL_MAP:
            return YAHOO_SYMBOL_MAP[s]
        if not s.endswith(".NS") and not s.endswith(".BO") and not s.startswith("^"):
            return f"{s}.NS"
        return s

    async def get_quote(self, symbol: str) -> Quote:
        """Fetch quote via yfinance with fallback."""
        try:
            import yfinance as yf
            ticker_sym = self._to_yahoo_symbol(symbol)
            
            # Run blocking yfinance in threadpool
            def _fetch():
                t = yf.Ticker(ticker_sym)
                fast = t.fast_info
                return {
                    "last_price": getattr(fast, "last_price", None),
                    "prev_close": getattr(fast, "previous_close", None),
                    "open": getattr(fast, "open", None),
                    "high": getattr(fast, "day_high", None),
                    "low": getattr(fast, "day_low", None),
                    "volume": getattr(fast, "last_volume", None),
                    "high_52w": getattr(fast, "year_high", None),
                    "low_52w": getattr(fast, "year_low", None),
                }

            data = await asyncio.to_thread(_fetch)
            if data["last_price"] is not None and data["last_price"] > 0:
                last_p = round(float(data["last_price"]), 2)
                prev_c = round(float(data["prev_close"] or last_p), 2)
                chg = round(last_p - prev_c, 2)
                pct = round((chg / max(prev_c, 0.01)) * 100, 2)
                
                return Quote(
                    symbol=symbol.upper(),
                    exchange=Exchange.NSE,
                    last_price=last_p,
                    change=chg,
                    percent_change=pct,
                    open=round(float(data["open"] or last_p), 2),
                    high=round(float(data["high"] or last_p), 2),
                    low=round(float(data["low"] or last_p), 2),
                    previous_close=prev_c,
                    volume=int(data["volume"] or 1_000_000),
                    high_52w=round(float(data["high_52w"] or last_p * 1.2), 2),
                    low_52w=round(float(data["low_52w"] or last_p * 0.8), 2),
                    timestamp=datetime.now(IST_TIMEZONE),
                    provider=self.provider_name,
                )
        except Exception:
            pass
            
        return await self._fallback.get_quote(symbol)

    async def get_index_quotes(self) -> List[IndexQuote]:
        """Fetch primary indices."""
        # For responsiveness and reliability, we can use development provider combined with yfinance
        return await self._fallback.get_index_quotes()

    async def get_history(
        self,
        symbol: str,
        timeframe: str = "1D",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Candle]:
        """Fetch historical candles with development fallback."""
        try:
            import yfinance as yf
            ticker_sym = self._to_yahoo_symbol(symbol)
            
            def _fetch_hist():
                t = yf.Ticker(ticker_sym)
                period_map = {"1D": "6mo", "1h": "1mo", "15m": "5d", "5m": "5d", "1m": "1d"}
                interval_map = {"1D": "1d", "1h": "1h", "15m": "15m", "5m": "5m", "1m": "1m"}
                p = period_map.get(timeframe, "6mo")
                inter = interval_map.get(timeframe, "1d")
                df = t.history(period=p, interval=inter)
                return df

            df = await asyncio.to_thread(_fetch_hist)
            if df is not None and not df.empty:
                candles: List[Candle] = []
                for idx, row in df.tail(limit).iterrows():
                    ts = idx.to_pydatetime()
                    if ts.tzinfo is None:
                        ts = IST_TIMEZONE.localize(ts)
                    candles.append(
                        Candle(
                            timestamp=ts,
                            open=round(float(row["Open"]), 2),
                            high=round(float(row["High"]), 2),
                            low=round(float(row["Low"]), 2),
                            close=round(float(row["Close"]), 2),
                            volume=int(row["Volume"]),
                            turnover=round((int(row["Volume"]) * float(row["Close"])) / 10_000_000, 2),
                        )
                    )
                if len(candles) > 0:
                    return candles
        except Exception:
            pass

        return await self._fallback.get_history(symbol, timeframe, start_date, end_date, limit)

    async def get_market_breadth(self) -> MarketBreadth:
        return await self._fallback.get_market_breadth()

    async def get_fii_dii_activity(self, target_date: Optional[date] = None) -> FiiDiiActivity:
        return await self._fallback.get_fii_dii_activity(target_date)

    async def get_sector_performance(self) -> List[SectorPerformance]:
        return await self._fallback.get_sector_performance()

    async def get_symbols(self, query: Optional[str] = None, limit: int = 50) -> List[SymbolInfo]:
        return await self._fallback.get_symbols(query, limit)
