"""
Per-analyst calibration on closed trades.

The trader combines four analyst signals with fixed weights. The auditor takes
closed trades whose deliberation snapshot includes the analyst signals at entry,
and computes for each analyst:
  - directional accuracy (did the sign of its signal match trade outcome?)
  - correlation of magnitude to realized PnL%

We then rebalance the weights so analysts with a track record get more say.
Weights are persisted to ops/analyst_weights.json; the trader reads them on
the next cycle. Bounded so no analyst ever exceeds 60% or goes below 5%.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any, Iterable
import json
import os

WEIGHTS_PATH = Path(os.getenv("OPS_WEIGHTS_PATH", "ops/analyst_weights.json"))
DEFAULT_WEIGHTS: Dict[str, float] = {
    "fundamentals": 0.25,
    "technicals": 0.40,
    "sentiment": 0.15,
    "macro": 0.20,
}
MIN_WEIGHT = 0.05
MAX_WEIGHT = 0.60


@dataclass
class AnalystScore:
    directional_correct: int = 0
    directional_total: int = 0
    signal_sum: float = 0.0
    pnl_sum: float = 0.0
    n: int = 0

    @property
    def accuracy(self) -> float:
        return self.directional_correct / max(1, self.directional_total)

    def performance_score(self) -> float:
        """Higher = better. In [0, 1]-ish."""
        # Directional accuracy dominates; correlation adds a small edge signal.
        acc = self.accuracy
        # Reward analysts whose signal moves with realized PnL (very rough proxy).
        if self.n > 0 and self.signal_sum != 0:
            avg_signal = self.signal_sum / self.n
            avg_pnl = self.pnl_sum / self.n
            corr_proxy = 1.0 if (avg_signal > 0) == (avg_pnl > 0) else 0.0
        else:
            corr_proxy = 0.5
        return 0.7 * acc + 0.3 * corr_proxy


def load_weights() -> Dict[str, float]:
    """Read weights (or defaults). Missing/invalid → defaults."""
    if not WEIGHTS_PATH.exists():
        return dict(DEFAULT_WEIGHTS)
    try:
        raw = json.loads(WEIGHTS_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return dict(DEFAULT_WEIGHTS)
        # Only accept known analyst keys.
        w = {k: float(raw.get(k, DEFAULT_WEIGHTS[k])) for k in DEFAULT_WEIGHTS}
        return _normalize_bounded(w)
    except Exception:
        return dict(DEFAULT_WEIGHTS)


def _normalize_bounded(w: Dict[str, float]) -> Dict[str, float]:
    """Clip to [MIN, MAX] then re-normalize to sum 1.0."""
    clipped = {k: min(MAX_WEIGHT, max(MIN_WEIGHT, float(v))) for k, v in w.items()}
    total = sum(clipped.values()) or 1.0
    return {k: round(v / total, 4) for k, v in clipped.items()}


def calibrate(closed_trades: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute new weights from an iterable of closed-trade records.

    Each record must have:
      - "pnl_pct": float
      - "analyst_signals_at_entry": {"fundamentals": s, "technicals": s, "sentiment": s, "macro": s}
    Records missing analyst_signals_at_entry are skipped.
    Returns {"weights": {...}, "scores": {...}, "sample_size": n}.
    """
    scores: Dict[str, AnalystScore] = {k: AnalystScore() for k in DEFAULT_WEIGHTS}
    n_used = 0
    for t in closed_trades:
        signals = t.get("analyst_signals_at_entry")
        if not signals:
            continue
        pnl = float(t.get("pnl_pct", 0.0))
        outcome_up = pnl > 0
        n_used += 1
        for analyst, ascore in scores.items():
            s = float(signals.get(analyst, 0.0))
            if abs(s) < 0.05:
                continue  # analyst had no directional opinion
            ascore.directional_total += 1
            if (s > 0) == outcome_up:
                ascore.directional_correct += 1
            ascore.signal_sum += s
            ascore.pnl_sum += pnl
            ascore.n += 1

    if n_used < 10:
        # Not enough data to overwrite priors; return current weights unchanged.
        return {
            "weights": load_weights(),
            "scores": {k: {"accuracy": v.accuracy, "n": v.n} for k, v in scores.items()},
            "sample_size": n_used,
            "note": "Insufficient sample (< 10) — keeping existing weights.",
        }

    perf = {k: v.performance_score() for k, v in scores.items()}
    # Blend 70% default prior with 30% performance to avoid whiplash on small samples.
    blended = {k: 0.7 * DEFAULT_WEIGHTS[k] + 0.3 * perf[k] for k in DEFAULT_WEIGHTS}
    new_weights = _normalize_bounded(blended)

    WEIGHTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    WEIGHTS_PATH.write_text(json.dumps(new_weights, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "weights": new_weights,
        "scores": {k: {"accuracy": round(v.accuracy, 3), "n": v.n} for k, v in scores.items()},
        "sample_size": n_used,
    }
