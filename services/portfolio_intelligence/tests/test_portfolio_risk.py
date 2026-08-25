"""
Unit tests for Portfolio Intelligence & VaR Engine.
"""

from services.portfolio_intelligence.risk_engine import PortfolioRiskEngine


def test_portfolio_var_and_stress_testing():
    engine = PortfolioRiskEngine()

    mock_holdings = [
        {"symbol": "RELIANCE", "quantity": 100, "average_price": 2500.0, "invested_value": 250000.0},
        {"symbol": "TCS", "quantity": 50, "average_price": 3800.0, "invested_value": 190000.0},
        {"symbol": "HDFCBANK", "quantity": 120, "average_price": 1600.0, "invested_value": 192000.0},
    ]

    analysis = engine.analyze_portfolio_risk(
        holdings=mock_holdings,
        portfolio_value=1_000_000.0,
    )

    assert analysis["portfolio_value"] == 1_000_000.0
    assert analysis["total_invested"] == 632000.0
    assert analysis["var_95_inr"] > 0
    assert analysis["var_99_inr"] > analysis["var_95_inr"]
    assert analysis["cvar_95_inr"] > analysis["var_95_inr"]
    assert len(analysis["sector_allocation"]) >= 2
    assert len(analysis["stress_tests"]) == 4
