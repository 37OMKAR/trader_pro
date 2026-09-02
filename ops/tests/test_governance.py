"""
Governance tests: kill switch, PM exposure caps, PM daily-loss halt, auditor
weight bounds, triggers. These tests must pass before every deploy.

They use temporary paths for ops/state.json + ops/limits.json + ops/analyst_weights.json
so they can't corrupt real state.
"""
import asyncio
import os
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture(autouse=True)
def _isolated_ops_paths(tmp_path, monkeypatch):
    monkeypatch.setenv("OPS_STATE_PATH", str(tmp_path / "state.json"))
    monkeypatch.setenv("OPS_LIMITS_PATH", str(tmp_path / "limits.json"))
    monkeypatch.setenv("OPS_WEIGHTS_PATH", str(tmp_path / "analyst_weights.json"))
    # Force re-import so module-level Path captures the new env.
    import importlib
    import ops.config, ops.state, services.auditor.calibrator
    importlib.reload(ops.config)
    importlib.reload(ops.state)
    importlib.reload(services.auditor.calibrator)
    yield


class _StubLLM:
    async def generate(self, *_a, **_kw) -> str:
        return "stub memo"


def _pm():
    from agents.execution.portfolio_manager import PortfolioManagerAgent
    return PortfolioManagerAgent(_StubLLM())


def _sample_proposal(symbol="RELIANCE", entry=100.0, stop=97.0):
    return {
        "symbol": symbol,
        "action": "BUY",
        "entry_price": entry,
        "stop_loss": stop,
        "target_1": entry * 1.06,
        "target_2": entry * 1.10,
        "suggested_allocation_pct": 10.0,
    }


def _risk_approved(qty=100):
    return {
        "approved": True,
        "max_approved_shares": qty,
        "summary": "ok",
    }


def _portfolio(cash=1_000_000.0, positions=None):
    return {"cash": cash, "total_value": cash, "positions": positions or []}


def test_kill_switch_halted_blocks_new_orders():
    from ops import state as ops_state
    ops_state.halt("test")
    pm = _pm()
    decision = asyncio.run(pm.authorize_trade(
        "RELIANCE", _sample_proposal(), _risk_approved(), _portfolio()
    ))
    assert decision["status"] == "REJECT"
    assert decision["reject_code"] == "KILL_SWITCH_HALTED"


def test_symbol_not_whitelisted_is_rejected():
    pm = _pm()
    decision = asyncio.run(pm.authorize_trade(
        "NOTLISTED", _sample_proposal("NOTLISTED"), _risk_approved(), _portfolio()
    ))
    assert decision["status"] == "REJECT"
    assert decision["reject_code"] == "SYMBOL_NOT_WHITELISTED"


def test_position_cap_forces_resize():
    from ops import state as ops_state
    ops_state.resume()
    pm = _pm()
    # Ask for 5000 shares × ₹100 = ₹500,000 on ₹1M NAV = 50% (way over 15% cap).
    decision = asyncio.run(pm.authorize_trade(
        "RELIANCE", _sample_proposal(entry=100.0),
        _risk_approved(qty=5000), _portfolio(),
    ))
    assert decision["status"] == "RESIZE"
    assert decision["order_details"]["quantity"] < 5000
    # 15% of 1M / 100 = 1500 max
    assert decision["order_details"]["quantity"] <= 1500


def test_sector_cap_forces_resize():
    from ops import state as ops_state
    ops_state.resume()
    pm = _pm()
    # Existing IT exposure: 2 x TCS × 100 shares × ₹1500 = ₹300,000 = 30% of 1M
    # Sector cap is 30%; adding INFY should be rejected or heavily resized.
    existing = [{"symbol": "TCS", "current_value": 300_000.0}]
    decision = asyncio.run(pm.authorize_trade(
        "INFY", _sample_proposal("INFY", entry=1500.0),
        _risk_approved(qty=100),
        _portfolio(cash=700_000.0, positions=existing),
    ))
    # Either REJECT (sector already full) or a very small RESIZE
    assert decision["status"] in ("REJECT", "RESIZE")
    if decision["status"] == "RESIZE":
        assert decision["order_details"]["quantity"] < 100


def test_daily_loss_budget_triggers_halt():
    from ops import state as ops_state
    ops_state.resume()
    # NAV = 1M, cap = 2% = ₹20k. Record a ₹-25k realized loss.
    ops_state.record_realized_pnl(-25_000.0)
    pm = _pm()
    decision = asyncio.run(pm.authorize_trade(
        "RELIANCE", _sample_proposal(), _risk_approved(), _portfolio()
    ))
    assert decision["status"] == "REJECT"
    assert decision["reject_code"] == "DAILY_LOSS_BUDGET_HIT"
    # Confirm the halt persisted.
    assert ops_state.get().halted is True


def test_quarantine_after_consecutive_losses():
    from ops import config as ops_config
    from ops import state as ops_state
    cfg = ops_config.load()
    ops_state.resume()
    for _ in range(cfg.quarantine_after_losses):
        ops_state.note_trade_outcome("RELIANCE", is_win=False,
                                     quarantine_after=cfg.quarantine_after_losses,
                                     quarantine_days=cfg.quarantine_days)
    assert ops_state.is_quarantined("RELIANCE") is True
    pm = _pm()
    decision = asyncio.run(pm.authorize_trade(
        "RELIANCE", _sample_proposal(), _risk_approved(), _portfolio()
    ))
    assert decision["status"] == "REJECT"
    assert decision["reject_code"] == "SYMBOL_QUARANTINED"


def test_auditor_returns_defaults_on_small_sample():
    from services.auditor.calibrator import calibrate, DEFAULT_WEIGHTS
    result = calibrate([])
    assert result["weights"] == DEFAULT_WEIGHTS
    assert result["sample_size"] == 0


def test_auditor_weight_bounds_hold_on_large_sample():
    from services.auditor.calibrator import calibrate, MIN_WEIGHT, MAX_WEIGHT
    # 20 trades where technicals is always right and macro is always wrong.
    trades = []
    for i in range(20):
        outcome = 5.0 if i % 2 == 0 else -3.0
        trades.append({
            "pnl_pct": outcome,
            "analyst_signals_at_entry": {
                "fundamentals": 0.1 if outcome > 0 else -0.1,
                "technicals": 0.5 if outcome > 0 else -0.5,
                "sentiment": 0.2 if outcome > 0 else -0.2,
                "macro": -0.5 if outcome > 0 else 0.5,   # inverted
            }
        })
    result = calibrate(trades)
    w = result["weights"]
    # No analyst should escape the bounds, and weights sum to ~1.
    for k, v in w.items():
        assert MIN_WEIGHT - 1e-6 <= v <= MAX_WEIGHT + 1e-6, f"{k}={v}"
    assert abs(sum(w.values()) - 1.0) < 1e-3
    # Macro was inverted — its weight should not exceed the default.
    assert w["macro"] <= 0.25 + 1e-6


def test_triggers_fire_on_gap_move():
    from apps.autonomous.triggers import fired
    def c(o, h, l, cl, v=1000):
        return SimpleNamespace(open=o, high=h, low=l, close=cl, volume=v)
    # Flat series then a gap.
    series = [c(100, 101, 99, 100) for _ in range(25)]
    series.append(c(103, 105, 103, 104))  # +4% gap up
    assert fired(series) in ("GAP_MOVE", "SMA20_CROSS_UP", "MOMENTUM_5D", "VOLUME_SHOCK")


def test_triggers_return_none_on_calm_market():
    from apps.autonomous.triggers import fired
    def c(o, h, l, cl, v=1000):
        return SimpleNamespace(open=o, high=h, low=l, close=cl, volume=v)
    calm = [c(100, 100.5, 99.5, 100 + 0.001 * i) for i in range(30)]
    assert fired(calm) is None
