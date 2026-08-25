"""
Unit tests for Feature Engine calculations and pipelines.
"""

import pytest
from packages.market_data.development_provider import DevelopmentMarketDataProvider
from services.feature_engine.calculator import FeatureCalculator
from services.feature_engine.pipeline import FeaturePipeline


@pytest.mark.anyio
async def test_feature_calculator_indicators():
    calc = FeatureCalculator()
    prices = [100.0 + i * 1.5 for i in range(30)]

    sma_20 = calc.calculate_sma(prices, 20)
    assert sma_20 is not None
    assert sma_20 > 0

    ema_20 = calc.calculate_ema(prices, 20)
    assert ema_20 is not None

    rsi_14 = calc.calculate_rsi(prices, 14)
    assert rsi_14 is not None
    assert 0.0 <= rsi_14 <= 100.0

    bb = calc.calculate_bollinger_bands(prices, 20)
    assert bb["upper"] is not None
    assert bb["upper"] > bb["middle"] > bb["lower"]


@pytest.mark.anyio
async def test_feature_pipeline_extraction():
    provider = DevelopmentMarketDataProvider()
    pipeline = FeaturePipeline()

    quote = await provider.get_quote("RELIANCE")
    candles = await provider.get_history("RELIANCE", timeframe="1D", limit=40)
    nifty_candles = await provider.get_history("NIFTY 50", timeframe="1D", limit=40)

    features = pipeline.extract_features("RELIANCE", quote, candles, nifty_candles)

    assert features["symbol"] == "RELIANCE"
    assert "price_features" in features
    assert "volume_features" in features
    assert "fundamental_features" in features
    assert features["price_features"]["rsi_14"] is not None
    assert features["price_features"]["sma_20"] is not None
