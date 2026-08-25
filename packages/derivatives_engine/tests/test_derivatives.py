"""
Unit tests for Black-Scholes Greeks and Option Chain Engine.
"""

import pytest
from packages.derivatives_engine.greeks import BlackScholesGreeks
from packages.derivatives_engine.option_chain import OptionChainEngine


def test_black_scholes_greeks_call_and_put():
    calc = BlackScholesGreeks()
    spot = 24500.0
    strike = 24500.0  # ATM
    t_years = 7.0 / 365.0  # 7 days to expiry
    iv = 0.15  # 15%

    ce = calc.calculate_greeks(spot, strike, t_years, iv, option_type="CE")
    pe = calc.calculate_greeks(spot, strike, t_years, iv, option_type="PE")

    assert ce["price"] > 0
    assert pe["price"] > 0
    assert 0.45 <= ce["delta"] <= 0.55
    assert -0.55 <= pe["delta"] <= -0.45
    assert ce["gamma"] > 0
    assert ce["theta"] < 0
    assert ce["vega"] > 0


def test_option_chain_generation():
    engine = OptionChainEngine()
    chain = engine.generate_option_chain("NIFTY 50", 24530.0, num_strikes=11)

    assert chain["symbol"] == "NIFTY 50"
    assert chain["atm_strike"] == 24550
    assert chain["pcr_oi"] > 0
    assert len(chain["strikes"]) == 11
    assert any(s["is_atm"] for s in chain["strikes"])
    
    first_strike = chain["strikes"][0]
    assert "call" in first_strike and "put" in first_strike
    assert first_strike["call"]["delta"] is not None
