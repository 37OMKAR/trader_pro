"""
Unit tests for Market Data Providers.
"""

import pytest
from packages.market_data.development_provider import DevelopmentMarketDataProvider


@pytest.mark.anyio
async def test_development_provider_quotes():
    provider = DevelopmentMarketDataProvider()
    quote = await provider.get_quote("RELIANCE")
    
    assert quote.symbol == "RELIANCE"
    assert quote.last_price > 0
    assert quote.open > 0
    assert quote.high >= quote.low
    assert quote.volume > 0


@pytest.mark.anyio
async def test_development_provider_indices():
    provider = DevelopmentMarketDataProvider()
    indices = await provider.get_index_quotes()
    
    symbols = [idx.symbol for idx in indices]
    assert "NIFTY 50" in symbols
    assert "SENSEX" in symbols
    assert "NIFTY BANK" in symbols
    assert "INDIA VIX" in symbols

    nifty = next(i for i in indices if i.symbol == "NIFTY 50")
    assert nifty.current_value > 20000.0


@pytest.mark.anyio
async def test_development_provider_history():
    provider = DevelopmentMarketDataProvider()
    candles = await provider.get_history("NIFTY 50", timeframe="1D", limit=30)
    
    assert len(candles) == 30
    for c in candles:
        assert c.high >= c.low
        assert c.high >= c.open
        assert c.high >= c.close
        assert c.volume > 0


@pytest.mark.anyio
async def test_market_breadth_and_fii_dii():
    provider = DevelopmentMarketDataProvider()
    breadth = await provider.get_market_breadth()
    assert breadth.advances > 0
    assert breadth.declines > 0
    assert breadth.total_traded_stocks == (breadth.advances + breadth.declines + breadth.unchanged)

    fii_dii = await provider.get_fii_dii_activity()
    assert fii_dii.fii_buy_gross > 0
    assert fii_dii.dii_buy_gross > 0
    assert fii_dii.total_institutional_net == round(fii_dii.fii_net + fii_dii.dii_net, 2)
