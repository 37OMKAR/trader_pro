"""
Integration tests for FastAPI Market Endpoints.
"""

import pytest
from starlette.testclient import TestClient
from apps.api.app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert "Market AI" in data["platform"]


def test_market_status(client):
    response = client.get("/api/v1/market/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "ist_time" in data
    assert "session_name" in data


def test_market_indices(client):
    response = client.get("/api/v1/market/indices")
    assert response.status_code == 200
    indices = response.json()
    assert len(indices) >= 4
    symbols = [idx["symbol"] for idx in indices]
    assert "NIFTY 50" in symbols
    assert "BANK NIFTY" in symbols or "NIFTY BANK" in symbols


def test_index_history(client):
    response = client.get("/api/v1/market/indices/NIFTY 50/history?timeframe=1D&limit=20")
    assert response.status_code == 200
    candles = response.json()
    assert len(candles) == 20
    assert "open" in candles[0]
    assert "close" in candles[0]
    assert "volume" in candles[0]


def test_market_breadth(client):
    response = client.get("/api/v1/market/breadth")
    assert response.status_code == 200
    data = response.json()
    assert data["advances"] > 0
    assert data["declines"] > 0


def test_fii_dii(client):
    response = client.get("/api/v1/market/fii-dii")
    assert response.status_code == 200
    data = response.json()
    assert "fii_net" in data
    assert "dii_net" in data


def test_sectors(client):
    response = client.get("/api/v1/market/sectors")
    assert response.status_code == 200
    sectors = response.json()
    assert len(sectors) > 0


def test_regime(client):
    response = client.get("/api/v1/market/regime")
    assert response.status_code == 200
    regime = response.json()
    assert "regime" in regime
    assert "probability" in regime
    assert len(regime["drivers"]) > 0
