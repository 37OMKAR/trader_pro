"""
Integration tests for extended Market Intelligence REST endpoints:
Features, Regime, ML Predictions, and Deep Stock Details.
"""

import pytest
from starlette.testclient import TestClient
from apps.api.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_stock_features_endpoint(client):
    response = client.get("/api/v1/market/features/RELIANCE")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "RELIANCE"
    assert "price_features" in data
    assert "volume_features" in data
    assert "fundamental_features" in data
    assert data["price_features"]["rsi_14"] is not None


def test_stock_predictions_endpoint(client):
    response = client.get("/api/v1/market/predictions/TCS?horizon=5D")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "TCS"
    assert data["horizon"] == "5D"
    assert data["direction"] in ["UP", "DOWN", "NEUTRAL"]
    assert 0.0 <= data["probability"] <= 1.0


def test_recent_predictions_list_endpoint(client):
    response = client.get("/api/v1/market/predictions?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_stock_deep_details_endpoint(client):
    response = client.get("/api/v1/market/stocks/INFY/details")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "INFY"
    assert "quote" in data
    assert "features" in data
    assert "prediction" in data
    assert "shareholding_pattern" in data
