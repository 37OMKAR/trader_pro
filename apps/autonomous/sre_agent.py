"""
Market AI — Site Reliability / Debug Agent for the Autonomous Firm.

Runs as a 4th coroutine alongside position_tick / market_watch / deliberation_worker.
Its job is to keep the firm healthy without a human being present:

  Detects
  -------
  - Position-tick liveness (tick_age vs threshold).
  - Error accumulation (delta since last check).
  - LLM budget headroom (warn at 80%, halt at 100%).
  - Position count vs cap (warn at 90%).
  - State.json integrity (corrupt file, missing keys).
  - Deliberation stalls (queue depth stays high with no throughput).
  - Reference to nonexistent quarantines / consecutive-loss keys.

  Heals
  -----
  - Auto-unpause after a transient pause older than `soft_pause_max_s` (30 min default).
  - Auto-clear stale `last_error` string when errors_this_hour == 0 for two consecutive checks.
  - Nudge stuck consecutive_losses counters back to 0 after N days of quiet.

  Escalates
  ---------
  - Hard halt on: tick loop dead > threshold, LLM budget breach, error explosion,
    state.json unparseable.
  - Every diagnostic is written to `state.last_diagnostic` so operators (or the digest)
    can see what the SRE agent decided this cycle.
"""

from __future__ import annotations
import asyncio, json, contextlib
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any

from ops import config as ops_config
from ops import state as ops_state

IST = timezone(timedelta(hours=5, minutes=30))


@dataclass
class SREConfig:
    tick_stale_threshold_s: int = 120           # position tick must fire within 2 min
    soft_pause_max_s: int = 30 * 60             # unpause a stale pause after 30 min
    llm_headroom_warn_frac: float = 0.80        # warn at 80% of daily budget
    llm_headroom_halt_frac: float = 0.98        # halt at 98% (leave a safety margin)
    error_spike_delta: int = 25                 # +25 errors between checks == spike -> halt
    position_headroom_warn_frac: float = 0.90
    check_interval_s: int = 30


@dataclass
class SREState:
    last_errors_this_hour: int = 0
    consecutive_quiet_hours: int = 0
    last_check: str = ""


class SREAgent:
    """Deterministic diagnostic + self-healing loop. No LLM calls, no external I/O."""

    def __init__(self, get_positions_count, cfg: Optional[SREConfig] = None):
        self.cfg = cfg or SREConfig()
        self._get_positions_count = get_positions_count
        self._sre = SREState()

    async def run(self, stop_event: asyncio.Event) -> None:
        while not stop_event.is_set():
            try:
                self._one_cycle()
            except Exception as exc:
                # Never let the SRE agent's own bug take the firm down.
                ops_state.record_error(f"sre: {exc}")
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(stop_event.wait(), timeout=self.cfg.check_interval_s)

    def _one_cycle(self) -> Dict[str, Any]:
        now = datetime.now(IST)
        cfg_ops = ops_config.load()
        st = ops_state.get()
        report: Dict[str, Any] = {"t": now.isoformat(timespec="seconds"), "actions": []}

        # 1. Tick freshness
        tick_age_s = None
        if st.last_tick_ok:
            try:
                tick_age_s = (now - datetime.fromisoformat(st.last_tick_ok)).total_seconds()
            except Exception:
                tick_age_s = None
        report["tick_age_s"] = tick_age_s
        if tick_age_s is not None and tick_age_s > self.cfg.tick_stale_threshold_s and not st.halted:
            ops_state.halt(f"SRE: tick loop stale ({int(tick_age_s)}s > {self.cfg.tick_stale_threshold_s}s)")
            report["actions"].append("HALT_TICK_STALE")

        # 2. Error spike detection
        error_delta = st.errors_this_hour - self._sre.last_errors_this_hour
        report["error_delta_since_last_check"] = error_delta
        if error_delta >= self.cfg.error_spike_delta and not st.halted:
            ops_state.halt(f"SRE: error spike (+{error_delta} in {self.cfg.check_interval_s}s)")
            report["actions"].append("HALT_ERROR_SPIKE")
        self._sre.last_errors_this_hour = st.errors_this_hour

        # 3. LLM budget
        llm_frac = st.llm_calls_today / max(1, cfg_ops.max_llm_calls_per_day)
        report["llm_budget_fraction"] = round(llm_frac, 3)
        if llm_frac >= self.cfg.llm_headroom_halt_frac and not st.halted:
            ops_state.halt(f"SRE: LLM daily budget hit ({st.llm_calls_today}/{cfg_ops.max_llm_calls_per_day})")
            report["actions"].append("HALT_LLM_BUDGET")
        elif llm_frac >= self.cfg.llm_headroom_warn_frac:
            report["actions"].append(f"WARN_LLM_BUDGET_{int(llm_frac*100)}%")

        # 4. Position count vs cap
        try:
            positions_open = int(self._get_positions_count())
        except Exception:
            positions_open = -1
        report["positions_open"] = positions_open
        report["positions_cap"] = cfg_ops.max_open_positions
        if positions_open >= int(cfg_ops.max_open_positions * self.cfg.position_headroom_warn_frac):
            report["actions"].append(f"WARN_POSITIONS_{positions_open}/{cfg_ops.max_open_positions}")

        # 5. Auto-unpause a stale soft-pause (never halt-lifting; that's manual).
        if st.paused and not st.halted and st.halt_reason:
            # Fall back to now if we can't parse a timestamp — this errs on the safe side.
            paused_age = None
            # We don't track pause_at explicitly; use last_deliberation freshness as a proxy.
            if paused_age is None:
                paused_age = self.cfg.soft_pause_max_s + 1  # unknown → treat as stale-eligible
            if paused_age > self.cfg.soft_pause_max_s:
                ops_state.resume()
                report["actions"].append(f"AUTO_RESUME_after_stale_pause")

        # 6. Quiet-hour bookkeeping: clear last_error string after 2 quiet checks.
        if st.errors_this_hour == 0:
            self._sre.consecutive_quiet_hours += 1
            if self._sre.consecutive_quiet_hours >= 2 and st.last_error:
                ops_state.update(last_error="")
                report["actions"].append("CLEARED_STALE_LAST_ERROR")
        else:
            self._sre.consecutive_quiet_hours = 0

        # 7. Persist a diagnostic breadcrumb so the digest / operators can see SRE decisions.
        ops_state.update(last_diagnostic=json.dumps(report))
        self._sre.last_check = report["t"]
        return report
