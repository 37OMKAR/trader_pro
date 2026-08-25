"""
Market AI — Development / High-Fidelity Simulator Market Data Provider
Provides deterministic, high-fidelity Indian market quotes, historical candlesticks,
indices, FII/DII activity, and sector breadth without external paid API dependencies.
"""

import math
import random
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict
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
from packages.market_calendar.calendar import IST_TIMEZONE


# Universe of Top Indian Equities
INDIAN_EQUITY_UNIVERSE = [
    {"symbol": "RELIANCE", "name": "Reliance Industries Ltd", "sector": "Energy", "base_price": 2980.50, "lot": 250},
    {"symbol": "TCS", "name": "Tata Consultancy Services Ltd", "sector": "IT", "base_price": 4120.00, "lot": 175},
    {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "sector": "Banking", "base_price": 1680.25, "lot": 550},
    {"symbol": "INFY", "name": "Infosys Ltd", "sector": "IT", "base_price": 1845.60, "lot": 400},
    {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "sector": "Banking", "base_price": 1240.80, "lot": 700},
    {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd", "sector": "Telecom", "base_price": 1580.00, "lot": 475},
    {"symbol": "ITC", "name": "ITC Ltd", "sector": "FMCG", "base_price": 492.40, "lot": 1600},
    {"symbol": "SBIN", "name": "State Bank of India", "sector": "Banking", "base_price": 825.10, "lot": 750},
    {"symbol": "LICI", "name": "Life Insurance Corp of India", "sector": "Financials", "base_price": 995.00, "lot": 300},
    {"symbol": "HINDUNILVR", "name": "Hindustan Unilever Ltd", "sector": "FMCG", "base_price": 2720.00, "lot": 300},
    {"symbol": "LT", "name": "Larsen & Toubro Ltd", "sector": "Infrastructure", "base_price": 3650.00, "lot": 175},
    {"symbol": "BAJFINANCE", "name": "Bajaj Finance Ltd", "sector": "Financials", "base_price": 7180.00, "lot": 125},
    {"symbol": "MARUTI", "name": "Maruti Suzuki India Ltd", "sector": "Automobile", "base_price": 12450.00, "lot": 50},
    {"symbol": "SUNPHARMA", "name": "Sun Pharmaceutical Industries", "sector": "Pharma", "base_price": 1790.00, "lot": 350},
    {"symbol": "TATAMOTORS", "name": "Tata Motors Ltd", "sector": "Automobile", "base_price": 980.00, "lot": 575},
    {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank Ltd", "sector": "Banking", "base_price": 1795.00, "lot": 400},
    {"symbol": "AXISBANK", "name": "Axis Bank Ltd", "sector": "Banking", "base_price": 1185.00, "lot": 625},
    {"symbol": "TITAN", "name": "Titan Company Ltd", "sector": "Consumer", "base_price": 3480.00, "lot": 175},
    {"symbol": "NTPC", "name": "NTPC Ltd", "sector": "Energy", "base_price": 395.00, "lot": 1500},
    {"symbol": "ONGC", "name": "Oil & Natural Gas Corp Ltd", "sector": "Energy", "base_price": 288.00, "lot": 2250},
    {"symbol": "ADANIENT", "name": "Adani Enterprises Ltd", "sector": "Metals & Mining", "base_price": 2980.00, "lot": 300},
    {"symbol": "ADANIPORTS", "name": "Adani Ports and SEZ Ltd", "sector": "Infrastructure", "base_price": 1410.00, "lot": 400},
    {"symbol": "TATASTEEL", "name": "Tata Steel Ltd", "sector": "Metals & Mining", "base_price": 152.50, "lot": 5500},
    {"symbol": "POWERGRID", "name": "Power Grid Corp of India", "sector": "Energy", "base_price": 320.00, "lot": 1800},
    {"symbol": "M&M", "name": "Mahindra & Mahindra Ltd", "sector": "Automobile", "base_price": 2860.00, "lot": 200},
]

# Benchmark Indices
INDIAN_INDICES = [
    {"symbol": "NIFTY 50", "name": "NIFTY 50", "base_price": 24850.50, "prev_close": 24780.00},
    {"symbol": "SENSEX", "name": "BSE SENSEX 30", "base_price": 81550.00, "prev_close": 81320.00},
    {"symbol": "NIFTY BANK", "name": "NIFTY BANK", "base_price": 52140.00, "prev_close": 51950.00},
    {"symbol": "FINNIFTY", "name": "NIFTY FINANCIAL SERVICES", "base_price": 23600.00, "prev_close": 23510.00},
    {"symbol": "MIDCPNIFTY", "name": "NIFTY MIDCAP SELECT", "base_price": 12850.00, "prev_close": 12790.00},
    {"symbol": "INDIA VIX", "name": "INDIA VOLATILITY INDEX", "base_price": 13.45, "prev_close": 13.80},
]

# Sector Index Map
SECTORS_DATA = [
    {"sector_name": "NIFTY BANK", "symbol": "NIFTY BANK", "base": 52140.0, "pct": 0.85, "top": "HDFCBANK", "weight": 33.5},
    {"sector_name": "NIFTY IT", "symbol": "NIFTY IT", "base": 41850.0, "pct": 1.24, "top": "TCS", "weight": 14.2},
    {"sector_name": "NIFTY AUTO", "symbol": "NIFTY AUTO", "base": 24600.0, "pct": -0.32, "top": "M&M", "weight": 7.8},
    {"sector_name": "NIFTY PHARMA", "symbol": "NIFTY PHARMA", "base": 21900.0, "pct": 0.45, "top": "SUNPHARMA", "weight": 4.5},
    {"sector_name": "NIFTY FMCG", "symbol": "NIFTY FMCG", "base": 61200.0, "pct": 0.15, "top": "ITC", "weight": 8.9},
    {"sector_name": "NIFTY METAL", "symbol": "NIFTY METAL", "base": 9250.0, "pct": -0.75, "top": "TATASTEEL", "weight": 3.8},
    {"sector_name": "NIFTY ENERGY", "symbol": "NIFTY ENERGY", "base": 40100.0, "pct": 0.62, "top": "RELIANCE", "weight": 12.1},
    {"sector_name": "NIFTY INFRA", "symbol": "NIFTY INFRA", "base": 8650.0, "pct": 0.38, "top": "LT", "weight": 5.4},
    {"sector_name": "NIFTY REALTY", "symbol": "NIFTY REALTY", "base": 1040.0, "pct": 1.55, "top": "DLF", "weight": 1.6},
]


class DevelopmentMarketDataProvider(MarketDataProvider):
    """High-fidelity simulator provider producing realistic Indian market numbers."""

    def __init__(self, seed: int = 42):
        self._seed = seed
        self._price_offsets: Dict[str, float] = {}

    @property
    def provider_name(self) -> str:
        return "DevelopmentMarketDataProvider"

    def _get_live_fluctuation(self, symbol: str, base: float, volatility: float = 0.004) -> float:
        """Applies a smooth micro-fluctuation to simulate live ticks."""
        current_sec = datetime.now().second + datetime.now().microsecond / 1_000_000
        hash_val = sum(ord(c) for c in symbol)
        cycle = math.sin((current_sec + hash_val) * 0.5)
        offset = base * volatility * cycle * 0.5
        return round(base + offset, 2)

    async def get_quote(self, symbol: str) -> Quote:
        """Generate realistic quote for an equity or index."""
        symbol_upper = symbol.upper().replace(".NS", "").replace("^", "")
        
        # Check in equities
        stock = next((s for s in INDIAN_EQUITY_UNIVERSE if s["symbol"] == symbol_upper), None)
        if stock:
            base = stock["base_price"]
            current_price = self._get_live_fluctuation(symbol_upper, base, 0.008)
            prev_close = round(base * 0.992, 2)
            change = round(current_price - prev_close, 2)
            pct_change = round((change / prev_close) * 100, 2)
            day_high = round(max(current_price, base * 1.012), 2)
            day_low = round(min(current_price, base * 0.988), 2)
            open_p = round(base * 0.996, 2)
            vol = random.randint(1_200_000, 8_500_000)

            return Quote(
                symbol=symbol_upper,
                exchange=Exchange.NSE,
                company_name=stock["name"],
                last_price=current_price,
                change=change,
                percent_change=pct_change,
                open=open_p,
                high=day_high,
                low=day_low,
                previous_close=prev_close,
                volume=vol,
                value=round((vol * current_price) / 10_000_000, 2),  # In Crores
                vwap=round((day_high + day_low + current_price) / 3, 2),
                high_52w=round(base * 1.25, 2),
                low_52w=round(base * 0.78, 2),
                timestamp=datetime.now(IST_TIMEZONE),
                provider=self.provider_name,
            )

        # Check in indices
        idx = next((i for i in INDIAN_INDICES if i["symbol"] == symbol_upper or i["symbol"].replace(" ", "") == symbol_upper), None)
        base = idx["base_price"] if idx else 25000.0
        prev_close = idx["prev_close"] if idx else 24900.0
        current_price = self._get_live_fluctuation(symbol_upper, base, 0.003)
        change = round(current_price - prev_close, 2)
        pct_change = round((change / prev_close) * 100, 2)

        return Quote(
            symbol=symbol_upper,
            exchange=Exchange.NSE,
            company_name=idx["name"] if idx else symbol_upper,
            last_price=current_price,
            change=change,
            percent_change=pct_change,
            open=round(prev_close * 1.002, 2),
            high=round(max(current_price, base * 1.006), 2),
            low=round(min(current_price, base * 0.994), 2),
            previous_close=prev_close,
            volume=random.randint(150_000_000, 450_000_000),
            timestamp=datetime.now(IST_TIMEZONE),
            provider=self.provider_name,
        )

    async def get_index_quotes(self) -> List[IndexQuote]:
        """Fetch quotes for all primary benchmark Indian indices."""
        results: List[IndexQuote] = []
        for idx in INDIAN_INDICES:
            sym = idx["symbol"]
            base = idx["base_price"]
            prev_close = idx["prev_close"]
            current_price = self._get_live_fluctuation(sym, base, 0.004)
            change = round(current_price - prev_close, 2)
            pct_change = round((change / prev_close) * 100, 2)
            
            results.append(
                IndexQuote(
                    symbol=sym,
                    name=idx["name"],
                    current_value=current_price,
                    change=change,
                    percent_change=pct_change,
                    open=round(prev_close * 1.001, 2),
                    high=round(max(current_price, base * 1.005), 2),
                    low=round(min(current_price, base * 0.995), 2),
                    previous_close=prev_close,
                    advances=34 if "NIFTY" in sym else None,
                    declines=16 if "NIFTY" in sym else None,
                    timestamp=datetime.now(IST_TIMEZONE),
                )
            )
        return results

    async def get_history(
        self,
        symbol: str,
        timeframe: str = "1D",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Candle]:
        """
        Generate realistic historical OHLCV candlestick series.
        Uses Geometric Brownian Motion + mean-reverting trend dynamics.
        """
        symbol_upper = symbol.upper().replace(".NS", "").replace("^", "")
        
        # Determine base price
        stock = next((s for s in INDIAN_EQUITY_UNIVERSE if s["symbol"] == symbol_upper), None)
        idx = next((i for i in INDIAN_INDICES if i["symbol"] == symbol_upper), None)
        
        if stock:
            base_price = stock["base_price"]
            daily_vol = 0.018
        elif idx:
            base_price = idx["base_price"]
            daily_vol = 0.010
        else:
            base_price = 1000.0
            daily_vol = 0.015

        now = datetime.now(IST_TIMEZONE)
        candles: List[Candle] = []

        # Determine interval timedelta
        if timeframe in ["1m", "1M"]:
            delta = timedelta(minutes=1)
        elif timeframe in ["5m", "5M"]:
            delta = timedelta(minutes=5)
        elif timeframe in ["15m", "15M"]:
            delta = timedelta(minutes=15)
        elif timeframe in ["1h", "1H"]:
            delta = timedelta(hours=1)
        else:
            delta = timedelta(days=1)

        # Generate candles backwards from now
        current_time = now - (delta * limit)
        current_close = base_price * 0.88  # Started lower for positive general trend

        random.seed(self._seed + sum(ord(c) for c in symbol_upper))

        for i in range(limit):
            # Drift + stochastic shock
            drift = 0.0008  # slight upward bias for India growth story
            shock = random.gauss(0, daily_vol)
            pct_return = drift + shock
            
            candle_open = round(current_close, 2)
            candle_close = round(candle_open * (1 + pct_return), 2)
            
            # High and Low
            intra_vol = abs(random.gauss(0, daily_vol * 0.6))
            candle_high = round(max(candle_open, candle_close) * (1 + intra_vol), 2)
            candle_low = round(min(candle_open, candle_close) * (1 - intra_vol), 2)
            
            vol = int(random.randint(500_000, 4_000_000) * (1 + abs(pct_return) * 10))
            turnover = round((vol * candle_close) / 10_000_000, 2)

            candles.append(
                Candle(
                    timestamp=current_time,
                    open=candle_open,
                    high=candle_high,
                    low=candle_low,
                    close=candle_close,
                    volume=vol,
                    open_interest=int(vol * 0.4),
                    turnover=turnover,
                )
            )

            current_close = candle_close
            current_time += delta

        return candles

    async def get_market_breadth(self) -> MarketBreadth:
        """Generate realistic market breadth statistics."""
        adv = random.randint(1320, 1680)
        dec = random.randint(750, 1100)
        unch = random.randint(80, 140)
        total = adv + dec + unch
        ratio = round(adv / max(dec, 1), 2)

        return MarketBreadth(
            advances=adv,
            declines=dec,
            unchanged=unch,
            advance_decline_ratio=ratio,
            highs_52w=random.randint(140, 260),
            lows_52w=random.randint(15, 45),
            upper_circuits=random.randint(65, 120),
            lower_circuits=random.randint(20, 50),
            total_traded_stocks=total,
            timestamp=datetime.now(IST_TIMEZONE),
        )

    async def get_fii_dii_activity(self, target_date: Optional[date] = None) -> FiiDiiActivity:
        """Fetch institutional flows in INR Crores."""
        if target_date is None:
            target_date = datetime.now(IST_TIMEZONE).date()

        fii_buy = round(random.uniform(9500.0, 15500.0), 2)
        fii_sell = round(random.uniform(9000.0, 14800.0), 2)
        fii_net = round(fii_buy - fii_sell, 2)

        dii_buy = round(random.uniform(8500.0, 13800.0), 2)
        dii_sell = round(random.uniform(7000.0, 11500.0), 2)
        dii_net = round(dii_buy - dii_sell, 2)

        return FiiDiiActivity(
            date=target_date,
            fii_buy_gross=fii_buy,
            fii_sell_gross=fii_sell,
            fii_net=fii_net,
            dii_buy_gross=dii_buy,
            dii_sell_gross=dii_sell,
            dii_net=dii_net,
            total_institutional_net=round(fii_net + dii_net, 2),
            timestamp=datetime.now(IST_TIMEZONE),
        )

    async def get_sector_performance(self) -> List[SectorPerformance]:
        """Fetch sector performance metrics."""
        results: List[SectorPerformance] = []
        for sec in SECTORS_DATA:
            fluct = self._get_live_fluctuation(sec["symbol"], sec["base"], 0.003)
            base = sec["base"]
            pct = round(((fluct - base) / base) * 100 + sec["pct"], 2)
            chg = round(base * (pct / 100), 2)
            results.append(
                SectorPerformance(
                    sector_name=sec["sector_name"],
                    symbol=sec["symbol"],
                    current_value=round(base + chg, 2),
                    percent_change=pct,
                    change=chg,
                    top_contributor=sec["top"],
                    weight_pct=sec["weight"],
                )
            )
        return results

    async def get_symbols(self, query: Optional[str] = None, limit: int = 50) -> List[SymbolInfo]:
        """Search symbol universe."""
        results: List[SymbolInfo] = []
        for stock in INDIAN_EQUITY_UNIVERSE:
            if query:
                q = query.upper()
                if q not in stock["symbol"] and q not in stock["name"].upper():
                    continue
            results.append(
                SymbolInfo(
                    exchange=Exchange.NSE,
                    symbol=stock["symbol"],
                    company_name=stock["name"],
                    instrument_type=InstrumentType.EQUITY,
                    series="EQ",
                    sector=stock["sector"],
                    lot_size=stock["lot"],
                    tick_size=0.05,
                    active=True,
                )
            )
            if len(results) >= limit:
                break
        return results
