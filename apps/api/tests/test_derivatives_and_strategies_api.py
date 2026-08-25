"""
Integration tests for Derivatives & Strategy Lab REST endpoints.
"""

import pytest
from starlette.testclient import TestClient
from apps.api.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_option_chain_endpoint(client):
    response = client.get("/api/v1/derivatives/option-chain/NIFTY%2050?num_strikes=11")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "NIFTY 50"
    assert "strikes" in data
    assert len(data["strikes"]) == 11
    assert "pcr_oi" in data
    assert "max_pain" in data


def test_fno_universe_endpoint(client):
    response = client.get("/api/v1/derivatives/fno-universe")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 5
    assert any(item["symbol"] == "RELIANCE" for item in data)


def test_strategy_templates_endpoint(client):
    response = client.get("/api/v1/strategies/templates")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert "strategy_id" in data[0]


def test_natural_language_strategy_generator(client):
    response = client.post(
        "/api/v1/strategies/generate-from-prompt",
        json={"prompt": "Buy when RSI is oversold under 35 and price is above 50-DMA"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "entry_rules" in data
    assert len(data["entry_rules"]["conditions"]) >= 1


def test_strategy_backtest_endpoint(client):
    strategy_payload = {
        "strategy_id": "TEST_RSI_STRAT",
        "name": "Test RSI Strategy",
        "description": "Test strategy description",
        "version": "1.0.0",
        "asset_universe": ["RELIANCE"],
        "timeframe": "1D",
        "entry_rules": {
            "logical_operator": "AND",
            "conditions": [
                {"feature": "rsi_14", "operator": ">", "threshold": 45.0},
                {"feature": "close", "operator": ">", "threshold": "sma_20"},
            ],
        },
        "risk_management": {"stop_loss_pct": 2.0, "take_profit_pct": 5.0},
    }
    response = client.post(
        "/api/v1/strategies/backtest?symbol=RELIANCE&initial_capital=500000",
        json=strategy_payload,
    )
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "total_return_pct" in data["metrics"]
    assert "equity_curve" in data
