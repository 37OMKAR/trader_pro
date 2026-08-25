"""
Integration tests for Paper Trading and Strategy Tournaments REST endpoints.
"""

import pytest
from starlette.testclient import TestClient
from apps.api.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_paper_account_summary_endpoint(client):
    response = client.get("/api/v1/paper/account/summary")
    assert response.status_code == 200
    data = response.json()
    assert "account_id" in data
    assert "cash_balance" in data
    assert data["initial_capital"] == 1_000_000.0


def test_place_paper_order_endpoint(client):
    order_payload = {
        "symbol": "TCS",
        "action": "BUY",
        "quantity": 10,
        "order_type": "MARKET",
    }
    response = client.post("/api/v1/paper/orders/place", json=order_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FILLED"
    assert "order" in data
    assert data["order"]["symbol"] == "TCS"


def test_tournament_leaderboard_endpoint(client):
    response = client.get("/api/v1/tournaments/leaderboard?asset=RELIANCE")
    assert response.status_code == 200
    data = response.json()
    assert "leaderboard" in data
    assert len(data["leaderboard"]) >= 2
    assert data["leaderboard"][0]["rank"] == 1
    assert "strategy_score" in data["leaderboard"][0]
