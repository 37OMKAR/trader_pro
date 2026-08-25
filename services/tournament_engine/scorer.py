"""
Market AI — Quantitative Strategy Scoring Engine
Computes institutional composite StrategyScore across return, Sharpe, drawdown, stability, and out-of-sample robustness.
"""

from typing import Dict, Any


class StrategyScorer:
    """Calculates normalized 0-100 StrategyScore and performance tiers."""

    @staticmethod
    def calculate_strategy_score(metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formula from Section 31 of task.md:
        StrategyScore = 0.35 * ReturnScore + 0.25 * SharpeScore + 0.20 * DrawdownScore + 0.10 * StabilityScore + 0.10 * RobustnessScore
        """
        cagr = metrics.get("cagr_pct", metrics.get("total_return_pct", 0.0))
        sharpe = metrics.get("sharpe_ratio", 0.0)
        max_dd = metrics.get("max_drawdown_pct", 10.0)
        win_rate = metrics.get("win_rate_pct", 50.0)
        profit_factor = metrics.get("profit_factor", 1.0)

        # 1. Return Score (0-100, 25% CAGR = 100)
        ret_score = min(100.0, max(0.0, (cagr / 25.0) * 100.0))

        # 2. Sharpe Score (0-100, Sharpe 2.5 = 100)
        sharpe_score = min(100.0, max(0.0, (sharpe / 2.5) * 100.0))

        # 3. Drawdown Score (0-100, 0% DD = 100, 25% DD = 0)
        dd_score = max(0.0, 100.0 - (max_dd * 4.0))

        # 4. Stability Score (based on win rate & profit factor)
        stability_score = min(100.0, max(0.0, (win_rate * 0.7) + (min(profit_factor, 3.0) * 10.0)))

        # 5. Robustness Score
        robustness_score = 80.0 if sharpe >= 1.0 and max_dd < 15.0 else 55.0

        # Composite StrategyScore
        strategy_score = (
            (0.35 * ret_score)
            + (0.25 * sharpe_score)
            + (0.20 * dd_score)
            + (0.10 * stability_score)
            + (0.10 * robustness_score)
        )
        strategy_score = round(float(strategy_score), 1)

        # Tier & Badge Assignment
        if strategy_score >= 80.0:
            badge = "ELITE_ALPHA"
            tier = "Tier 1 — High Conviction Institutional"
        elif strategy_score >= 65.0:
            badge = "BALANCED_ALL_WEATHER"
            tier = "Tier 2 — Robust Diversifier"
        elif strategy_score >= 50.0:
            badge = "HIGH_MOMENTUM"
            tier = "Tier 3 — Cyclical Momentum"
        else:
            badge = "UNDER_EVALUATION"
            tier = "Tier 4 — Candidate for Mutation"

        return {
            "strategy_score": strategy_score,
            "badge": badge,
            "tier": tier,
            "sub_scores": {
                "return_score": round(ret_score, 1),
                "sharpe_score": round(sharpe_score, 1),
                "drawdown_score": round(dd_score, 1),
                "stability_score": round(stability_score, 1),
                "robustness_score": round(robustness_score, 1),
            },
        }
