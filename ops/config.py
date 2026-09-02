"""
Governance config for the autonomous trading company.

Hard limits are loaded from ops/limits.json (or defaults below).
The RUNNING AGENT MUST NEVER MUTATE THESE VALUES. Only a human writes to the JSON.
`load()` re-reads the file every call so the operator can tighten limits without a restart.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Any
import json
import os

LIMITS_PATH = Path(os.getenv("OPS_LIMITS_PATH", "ops/limits.json"))


@dataclass(frozen=True)
class GovernanceConfig:
    # Universe
    tradable_symbols: List[str] = field(default_factory=lambda: [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "TATAMOTORS"
    ])
    symbol_sector: Dict[str, str] = field(default_factory=lambda: {
        "RELIANCE": "ENERGY",
        "TCS": "IT",
        "INFY": "IT",
        "HDFCBANK": "BANKS",
        "TATAMOTORS": "AUTO",
    })

    # Position / exposure caps
    max_position_pct: float = 15.0            # any single symbol
    max_sector_pct: float = 30.0              # any single sector
    max_gross_exposure_pct: float = 80.0      # sum of position values / NAV
    max_open_positions: int = 8

    # Loss & risk budgets
    max_daily_loss_pct: float = 2.0           # halts new entries when hit
    max_trade_risk_pct: float = 1.0           # (entry-stop) * qty / NAV
    quarantine_after_losses: int = 3          # per symbol, blocks re-entry
    quarantine_days: int = 7

    # LLM cost meter
    max_llm_calls_per_hour: int = 200
    max_llm_calls_per_day: int = 2000

    # Loop cadences (seconds)
    market_watch_interval_s: int = 300
    position_tick_interval_s: int = 60
    deliberation_cooldown_s: int = 3600       # per-symbol re-deliberation lockout

    # Circuit breakers
    max_error_rate_per_hour: int = 20

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True)


def _from_dict(d: Dict[str, Any]) -> GovernanceConfig:
    """Build a config from arbitrary dict, silently dropping unknown keys."""
    valid = {f for f in GovernanceConfig.__dataclass_fields__}
    filtered = {k: v for k, v in d.items() if k in valid}
    return GovernanceConfig(**filtered)


def load() -> GovernanceConfig:
    """Read limits from disk each call. Falls back to defaults if the file is missing/invalid."""
    if not LIMITS_PATH.exists():
        return GovernanceConfig()
    try:
        raw = json.loads(LIMITS_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return GovernanceConfig()
        return _from_dict(raw)
    except Exception:
        # Never crash the agent because someone wrote a bad JSON — fall back to safe defaults.
        return GovernanceConfig()


def write_defaults() -> Path:
    """Utility for operators: write the current defaults to LIMITS_PATH."""
    LIMITS_PATH.parent.mkdir(parents=True, exist_ok=True)
    LIMITS_PATH.write_text(GovernanceConfig().to_json(), encoding="utf-8")
    return LIMITS_PATH
