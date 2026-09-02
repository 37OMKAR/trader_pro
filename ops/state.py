"""
Mutable operational state for the autonomous agent.

Two flags gate every action:
  paused=True  -> loops finish their current tick and idle. Position tick keeps running (protects stops).
  halted=True  -> no new orders. Position tick still runs. Manual reset only.

Counters (llm_calls_today, errors_this_hour) are kept here so they survive restarts.
Everything is stored in ops/state.json as human-readable JSON.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional
import json
import os
import threading

STATE_PATH = Path(os.getenv("OPS_STATE_PATH", "ops/state.json"))
_LOCK = threading.Lock()

IST = timezone(timedelta(hours=5, minutes=30))


@dataclass
class OpsState:
    paused: bool = False
    halted: bool = False
    halt_reason: str = ""
    watchlist: List[str] = field(default_factory=list)

    # LLM budget accounting (reset by _rollover_if_needed)
    llm_calls_today: int = 0
    llm_calls_hour_bucket: int = 0
    llm_calls_hour: int = 0
    day_bucket: str = ""                 # ISO date, IST
    hour_bucket: str = ""                # ISO hour, IST

    # Error accounting for circuit breaker
    errors_this_hour: int = 0
    errors_hour_bucket: str = ""

    # Per-symbol quarantines
    quarantined: Dict[str, str] = field(default_factory=dict)   # symbol -> ISO expiry

    # Per-symbol consecutive losses (for quarantine trigger)
    consecutive_losses: Dict[str, int] = field(default_factory=dict)

    # De-dup: symbol -> last deliberation ISO timestamp
    last_deliberation: Dict[str, str] = field(default_factory=dict)

    # Daily loss tracking
    day_realized_pnl: float = 0.0
    day_start_nav: float = 0.0

    # Health
    last_tick_ok: str = ""
    last_error: str = ""
    last_diagnostic: str = ""     # last SRE agent report, JSON string

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def _now() -> datetime:
    return datetime.now(IST)


def _load() -> OpsState:
    if not STATE_PATH.exists():
        return OpsState()
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return OpsState(**{k: v for k, v in data.items() if k in OpsState.__dataclass_fields__})
    except Exception:
        return OpsState()


def _persist(state: OpsState) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".json.tmp")
    tmp.write_text(state.to_json(), encoding="utf-8")
    tmp.replace(STATE_PATH)


def _rollover_if_needed(state: OpsState) -> None:
    now = _now()
    day = now.date().isoformat()
    hour = f"{day}T{now.hour:02d}"
    if state.day_bucket != day:
        state.day_bucket = day
        state.llm_calls_today = 0
        state.day_realized_pnl = 0.0
        state.day_start_nav = 0.0
    if state.hour_bucket != hour:
        state.hour_bucket = hour
        state.llm_calls_hour = 0
    if state.errors_hour_bucket != hour:
        state.errors_hour_bucket = hour
        state.errors_this_hour = 0
    # Expire quarantines that have elapsed.
    expired = [s for s, exp in state.quarantined.items() if exp <= now.isoformat()]
    for s in expired:
        state.quarantined.pop(s, None)


def get() -> OpsState:
    with _LOCK:
        state = _load()
        _rollover_if_needed(state)
        _persist(state)
        return state


def update(**changes) -> OpsState:
    with _LOCK:
        state = _load()
        _rollover_if_needed(state)
        for k, v in changes.items():
            if k in OpsState.__dataclass_fields__:
                setattr(state, k, v)
        _persist(state)
        return state


def record_llm_call(n: int = 1) -> OpsState:
    with _LOCK:
        state = _load()
        _rollover_if_needed(state)
        state.llm_calls_today += n
        state.llm_calls_hour += n
        _persist(state)
        return state


def record_error(message: str = "") -> OpsState:
    with _LOCK:
        state = _load()
        _rollover_if_needed(state)
        state.errors_this_hour += 1
        state.last_error = f"{_now().isoformat()} {message}"[:500]
        _persist(state)
        return state


def record_tick_ok() -> OpsState:
    with _LOCK:
        state = _load()
        _rollover_if_needed(state)
        state.last_tick_ok = _now().isoformat()
        _persist(state)
        return state


def record_realized_pnl(delta: float) -> OpsState:
    with _LOCK:
        state = _load()
        _rollover_if_needed(state)
        state.day_realized_pnl += float(delta)
        _persist(state)
        return state


def note_deliberation(symbol: str) -> OpsState:
    with _LOCK:
        state = _load()
        _rollover_if_needed(state)
        state.last_deliberation[symbol.upper()] = _now().isoformat()
        _persist(state)
        return state


def note_trade_outcome(symbol: str, is_win: bool, quarantine_after: int, quarantine_days: int) -> OpsState:
    with _LOCK:
        state = _load()
        _rollover_if_needed(state)
        sym = symbol.upper()
        if is_win:
            state.consecutive_losses[sym] = 0
        else:
            state.consecutive_losses[sym] = state.consecutive_losses.get(sym, 0) + 1
            if state.consecutive_losses[sym] >= quarantine_after:
                state.quarantined[sym] = (_now() + timedelta(days=quarantine_days)).isoformat()
        _persist(state)
        return state


def halt(reason: str) -> OpsState:
    return update(halted=True, halt_reason=reason[:200])


def pause(reason: str = "") -> OpsState:
    return update(paused=True, halt_reason=reason[:200])


def resume() -> OpsState:
    return update(paused=False, halted=False, halt_reason="")


def deliberation_allowed(symbol: str, cooldown_s: int) -> bool:
    state = get()
    last = state.last_deliberation.get(symbol.upper())
    if not last:
        return True
    try:
        last_dt = datetime.fromisoformat(last)
    except Exception:
        return True
    return (_now() - last_dt).total_seconds() >= cooldown_s


def is_quarantined(symbol: str) -> bool:
    state = get()
    return symbol.upper() in state.quarantined


def can_open_orders() -> bool:
    state = get()
    return not (state.paused or state.halted)
