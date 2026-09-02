"""
Market AI — Main Trader Agent
Aggregates analyst signals + bull/bear scores into a directional decision.
Sizes the trade from ATR-based volatility (not from fixed % of price).
"""

from typing import Dict, Any, Optional
from agents.llm_provider import LLMClient
from agents.indicators import clamp

try:
    from services.auditor.calibrator import load_weights as _load_analyst_weights
except Exception:  # pragma: no cover - defensive fallback for import cycles
    def _load_analyst_weights():
        return {"fundamentals": 0.25, "technicals": 0.40, "sentiment": 0.15, "macro": 0.20}


class TraderAgent:
    """Trader whose action, stop, and target derive from actual signals and volatility."""

    def __init__(self, llm: LLMClient, min_conviction: float = 0.15):
        self.llm = llm
        self.name = "Lead Trader"
        self.min_conviction = min_conviction

    async def decide_trade(
        self,
        symbol: str,
        current_price: float,
        analyst_reports: Dict[str, Any],
        bull_case: Dict[str, Any],
        bear_case: Dict[str, Any],
        atr: Optional[float] = None,
    ) -> Dict[str, Any]:
        # Weighted analyst signal (weights from auditor calibration; falls back to defaults)
        weights = _load_analyst_weights()
        confs = {}
        contribs = {}
        for k, w in weights.items():
            rep = analyst_reports.get(k, {})
            s = float(rep.get("signal", 0.0))
            c = float(rep.get("confidence", 0.5))
            confs[k] = c
            contribs[k] = w * s * c
        analyst_score = sum(contribs.values())

        bull_score = float(bull_case.get("score", 0.0))
        bear_score = float(bear_case.get("score", 0.0))
        debate_score = bull_score - bear_score  # in [-1, +1]

        # Combine analysts + debate (analysts drive; debate reinforces or dampens)
        net_score = clamp(0.7 * analyst_score + 0.3 * debate_score)

        # Decision
        if net_score > self.min_conviction:
            action = "BUY"
        elif net_score < -self.min_conviction:
            action = "SELL"  # only meaningful if a position exists; orchestrator can degrade to HOLD
        else:
            action = "HOLD"

        # ATR-based risk: fall back to a % of price when ATR isn't available.
        atr_val = float(atr) if atr and atr > 0 else max(0.5, current_price * 0.02)
        entry_price = round(float(current_price), 2)

        # Wider stops when conviction is lower (2.0x ATR at 0.15 conviction, 1.2x ATR at 1.0 conviction)
        stop_mult = 2.0 - min(1.0, abs(net_score)) * 0.8
        # Target is 2.5x the stop distance (R:R ≥ 2.5)
        stop_dist = round(stop_mult * atr_val, 2)
        target_dist = round(2.5 * stop_dist, 2)

        if action == "BUY":
            stop_loss = round(entry_price - stop_dist, 2)
            target_1 = round(entry_price + target_dist, 2)
            target_2 = round(entry_price + target_dist * 1.6, 2)
        elif action == "SELL":
            stop_loss = round(entry_price + stop_dist, 2)
            target_1 = round(entry_price - target_dist, 2)
            target_2 = round(entry_price - target_dist * 1.6, 2)
        else:  # HOLD
            stop_loss = entry_price
            target_1 = entry_price
            target_2 = entry_price

        risk_per_share = abs(entry_price - stop_loss)
        reward_per_share = abs(target_1 - entry_price)
        rr_ratio = round(reward_per_share / max(risk_per_share, 0.01), 2)

        # Suggested allocation scales with conviction. Risk manager still caps this downstream.
        suggested_allocation_pct = round(min(15.0, max(0.0, abs(net_score) * 15.0)), 1)
        if action == "HOLD":
            suggested_allocation_pct = 0.0

        time_horizon = "2-4 Weeks (Swing Trade)" if abs(net_score) < 0.5 else "1-2 Weeks (Momentum Trade)"

        system_prompt = (
            "You are the Head Trader at a quantitative equity hedge fund. "
            "Given the numeric analyst and debate scores, justify the trade in 2-3 sentences."
        )
        user_prompt = (
            f"{symbol} at ₹{current_price}: net_score={net_score:+.2f}, action={action}, "
            f"entry ₹{entry_price}, stop ₹{stop_loss}, target ₹{target_1}, R:R 1:{rr_ratio}, "
            f"alloc {suggested_allocation_pct}%. Analyst contributions: {contribs}."
        )
        llm_rationale = await self.llm.generate(system_prompt, user_prompt)

        return {
            "agent": self.name,
            "symbol": symbol,
            "action": action,
            "net_score": round(net_score, 3),
            "analyst_score": round(analyst_score, 3),
            "debate_score": round(debate_score, 3),
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,
            "risk_reward_ratio": f"1:{rr_ratio}",
            "atr_used": atr_val,
            "suggested_allocation_pct": suggested_allocation_pct,
            "time_horizon": time_horizon,
            "rationale": (
                f"Weighted analyst score {analyst_score:+.2f}, debate delta {debate_score:+.2f} "
                f"=> net {net_score:+.2f} => {action}. ATR ₹{atr_val} sizing gives 1:{rr_ratio}."
            ),
            "llm_rationale": llm_rationale,
        }
