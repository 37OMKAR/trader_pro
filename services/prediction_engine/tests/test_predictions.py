"""
Unit tests for ML Prediction Engine and Registry.
"""

import pytest
from packages.market_data.development_provider import DevelopmentMarketDataProvider
from services.feature_engine.pipeline import FeaturePipeline
from services.prediction_engine.models import MLPredictionEngine
from services.prediction_engine.registry import PredictionRegistry
from apps.api.app.db.session import init_db


@pytest.mark.anyio
async def test_ml_prediction_generation():
    provider = DevelopmentMarketDataProvider()
    pipeline = FeaturePipeline()
    pred_engine = MLPredictionEngine()

    quote = await provider.get_quote("TCS")
    candles = await provider.get_history("TCS", limit=30)
    features = pipeline.extract_features("TCS", quote, candles)

    prediction = pred_engine.predict("TCS", features, horizon="5D")

    assert prediction["symbol"] == "TCS"
    assert prediction["direction"] in ["UP", "DOWN", "NEUTRAL"]
    assert 0.0 <= prediction["probability"] <= 1.0
    assert 0.0 <= prediction["confidence"] <= 1.0
    assert 1.0 <= prediction["risk_score"] <= 10.0
    assert prediction["horizon"] == "5D"
    assert len(prediction["drivers"]) > 0


@pytest.mark.anyio
async def test_prediction_registry_storage():
    await init_db()
    provider = DevelopmentMarketDataProvider()
    pipeline = FeaturePipeline()
    pred_engine = MLPredictionEngine()

    quote = await provider.get_quote("HDFCBANK")
    candles = await provider.get_history("HDFCBANK", limit=30)
    features = pipeline.extract_features("HDFCBANK", quote, candles)

    prediction = pred_engine.predict("HDFCBANK", features, horizon="20D")
    pred_id = await PredictionRegistry.record_prediction(prediction)
    assert pred_id is not None
    assert pred_id.startswith("PRED-HDFCBANK")

    recent = await PredictionRegistry.get_recent_predictions(symbol="HDFCBANK", limit=5)
    assert len(recent) >= 1
    assert recent[0]["symbol"] == "HDFCBANK"
