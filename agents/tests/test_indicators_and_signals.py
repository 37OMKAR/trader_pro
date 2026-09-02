"""
Tests for the shared indicator math and the signal-driven trader/reflector.
"""
import asyncio
import math
from types import SimpleNamespace

import pytest

from agents.indicators import (
    sma, rsi, atr, rolling_return_pct, volume_zscore, detect_regime, clamp,
)
from agents.execution.trader_agent import TraderAgent
from agents.reflection import Reflector


def _candle(o, h, l, c, v=1_000_000):
    return SimpleNamespace(open=o, high=h, low=l, close=c, volume=v)


def _bull_series(n=60, start=100.0):
    # Steadily rising close series with realistic H/L wicks.
    cs = []
    p = start
    for i in range(n):
        o = p
        c = p * 1.005
        h = max(o, c) * 1.003
        l = min(o, c) * 0.997
        cs.append(_candle(o, h, l, c))
        p = c
    return cs


def _bear_series(n=60, start=100.0):
    cs = []
    p = start
    for i in range(n):
        o = p
        c = p * 0.995
        h = max(o, c) * 1.003
        l = min(o, c) * 0.997
        cs.append(_candle(o, h, l, c))
        p = c
    return cs


def test_sma_matches_arithmetic_mean():
    cs = [_candle(0, 0, 0, float(x)) for x in range(1, 11)]
    assert sma(cs, 10) == round(sum(range(1, 11)) / 10, 4)


def test_rsi_rising_series_is_bullish_regime():
    cs = _bull_series(60)
    r = rsi(cs, 14)
    assert r is not None and r > 60


def test_rsi_falling_series_is_bearish_regime():
    cs = _bear_series(60)
    r = rsi(cs, 14)
    assert r is not None and r < 40


def test_atr_is_positive_for_any_series():
    cs = _bull_series(30)
    a = atr(cs, 14)
    assert a is not None and a > 0


def test_detect_regime_identifies_direction():
    assert detect_regime(_bull_series(60)) == "BULL"
    assert detect_regime(_bear_series(60)) == "BEAR"


def test_clamp_bounds_values():
    assert clamp(5.0) == 1.0
    assert clamp(-5.0) == -1.0
    assert clamp(0.3) == 0.3


class _StubLLM:
    async def generate(self, *_a, **_kw) -> str:
        return "stub"


def test_trader_derives_buy_from_positive_signals():
    trader = TraderAgent(_StubLLM(), min_conviction=0.1)
    analyst_reports = {
        "fundamentals": {"signal": 0.5, "confidence": 0.8},
        "technicals": {"signal": 0.6, "confidence": 0.9},
        "sentiment": {"signal": 0.3, "confidence": 0.7},
        "macro": {"signal": 0.4, "confidence": 0.8},
    }
    bull = {"score": 0.6}
    bear = {"score": 0.1}
    decision = asyncio.run(trader.decide_trade(
        symbol="X", current_price=100.0,
        analyst_reports=analyst_reports, bull_case=bull, bear_case=bear, atr=2.0,
    ))
    assert decision["action"] == "BUY"
    assert decision["stop_loss"] < 100.0
    assert decision["target_1"] > 100.0
    assert decision["suggested_allocation_pct"] > 0


def test_trader_derives_hold_from_mixed_signals():
    trader = TraderAgent(_StubLLM(), min_conviction=0.2)
    analyst_reports = {
        "fundamentals": {"signal": 0.05, "confidence": 0.5},
        "technicals": {"signal": -0.05, "confidence": 0.5},
        "sentiment": {"signal": 0.0, "confidence": 0.5},
        "macro": {"signal": 0.0, "confidence": 0.5},
    }
    decision = asyncio.run(trader.decide_trade(
        symbol="X", current_price=100.0,
        analyst_reports=analyst_reports,
        bull_case={"score": 0.1}, bear_case={"score": 0.1}, atr=2.0,
    ))
    assert decision["action"] == "HOLD"
    assert decision["suggested_allocation_pct"] == 0.0


def test_reflector_hydration_rebuilds_win_prob():
    Reflector.hydrate_from_records([
        {"symbol": "AAA", "raw_return_pct": 5.0, "alpha_vs_nifty": 2.0, "lesson_learned": "won"},
        {"symbol": "AAA", "raw_return_pct": -3.0, "alpha_vs_nifty": -1.0, "lesson_learned": "lost"},
        {"symbol": "AAA", "raw_return_pct": 4.0, "alpha_vs_nifty": 1.5, "lesson_learned": "won"},
    ])
    # 2 wins, 1 loss + Beta(3,3) prior => (3+2)/(3+2+3+1) = 5/9 ≈ 0.556
    p = Reflector.get_win_prob("AAA")
    assert abs(p - 5.0 / 9.0) < 1e-3
    stats = Reflector.stats()
    assert stats["trades_recorded"] == 3
    assert stats["wins"] == 2
