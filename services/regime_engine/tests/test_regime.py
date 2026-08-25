"""
Unit tests for Market Regime Classifier.
"""

import pytest
from packages.market_data.development_provider import DevelopmentMarketDataProvider
from services.regime_engine.classifier import MarketRegimeClassifier
from packages.shared_types.market_types import MarketRegime


@pytest.mark.anyio
async def test_regime_classification():
    provider = DevelopmentMarketDataProvider()
    classifier = MarketRegimeClassifier()

    indices = await provider.get_index_quotes()
    nifty = next(i for i in indices if i.symbol == "NIFTY 50")
    bank = next(i for i in indices if "BANK" in i.symbol)
    vix = next(i for i in indices if "VIX" in i.symbol)
    breadth = await provider.get_market_breadth()
    fii_dii = await provider.get_fii_dii_activity()

    regime_state = classifier.evaluate_regime(nifty, bank, vix, breadth, fii_dii)

    assert regime_state.regime in [
        MarketRegime.BULL,
        MarketRegime.BEAR,
        MarketRegime.RANGE,
        MarketRegime.HIGH_VOLATILITY,
    ]
    assert 0.5 <= regime_state.probability <= 1.0
    assert 0.5 <= regime_state.confidence <= 1.0
    assert len(regime_state.drivers) > 0
