"""
Market AI — Autonomous Strategy Evolution Agent
Critiques backtest weaknesses and autonomously breeds next-generation mutated strategies with immutable lineage.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from services.strategy_dsl.schema import StrategyDefinition, RuleGroup, ConditionRule, RiskManagementConfig
from services.backtest_engine.engine import BacktestEngine
from packages.market_calendar.calendar import IST_TIMEZONE


class StrategyEvolutionAgent:
    """Evaluates strategy flaws and breeds mutations, capped to prevent unbounded drift."""

    # Absolute bounds prevent runaway compounding on repeated generations.
    MAX_TAKE_PROFIT_PCT = 15.0
    MIN_STOP_LOSS_PCT = 1.0
    MAX_STOP_LOSS_PCT = 6.0
    MAX_GENERATIONS = 8

    def __init__(self):
        self.backtest_engine = BacktestEngine()

    def critique_and_evolve(
        self,
        strategy: StrategyDefinition,
        backtest_result: Dict[str, Any],
        candles: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyzes metrics, drafts institutional critique, and mutates strategy DSL parameters.
        """
        metrics = backtest_result.get("metrics", {})
        cagr = metrics.get("cagr_pct", 0.0)
        sharpe = metrics.get("sharpe_ratio", 0.0)
        max_dd = metrics.get("max_drawdown_pct", 0.0)
        win_rate = metrics.get("win_rate_pct", 50.0)
        profit_factor = metrics.get("profit_factor", 1.0)

        critiques: List[str] = []
        mutations_applied: List[str] = []

        # Clone current conditions
        new_conditions = [cond.model_copy() for cond in strategy.entry_rules.conditions]
        new_risk = strategy.risk_management.model_copy()

        # 1. Critique: High Drawdown
        if max_dd > 10.0:
            critiques.append(f"Excessive drawdown of {max_dd}% indicates stop-loss is too loose or entry criteria trigger in choppy regimes.")
            new_risk.stop_loss_pct = round(max(self.MIN_STOP_LOSS_PCT, new_risk.stop_loss_pct * 0.8), 1)
            mutations_applied.append(f"Tightened stop loss from {strategy.risk_management.stop_loss_pct}% to {new_risk.stop_loss_pct}%")
            
            # Add or refine volume filter
            has_vol = any(c.feature == "volume_zscore" for c in new_conditions)
            if not has_vol:
                new_conditions.append(ConditionRule(feature="volume_zscore", operator=">", threshold=1.1))
                mutations_applied.append("Added Volume Z-Score confirmation (>1.1) to avoid low-liquidity false breakouts.")

        # 2. Critique: Low Win Rate
        if win_rate < 50.0:
            critiques.append(f"Sub-optimal win rate ({win_rate}%) suggests false positive breakout triggers.")
            for cond in new_conditions:
                if cond.feature == "rsi_14" and cond.operator == "<":
                    old_th = float(cond.threshold)
                    cond.threshold = round(max(25.0, old_th - 4.0), 1)
                    mutations_applied.append(f"Deepened oversold RSI entry threshold from {old_th} to {cond.threshold} for better mean-reversion discount.")
                elif cond.feature == "rsi_14" and cond.operator == ">":
                    old_th = float(cond.threshold)
                    cond.threshold = round(min(70.0, old_th + 3.0), 1)
                    mutations_applied.append(f"Raised momentum RSI trigger from {old_th} to {cond.threshold} to ensure stronger price conviction.")

        # 3. Critique: Low Profit Factor / Sharpe
        if profit_factor < 1.6 or sharpe < 1.2:
            critiques.append(f"Modest profit factor ({profit_factor}x) and Sharpe ({sharpe}). Enhancing reward-to-risk multiplier.")
            new_tp = round(min(self.MAX_TAKE_PROFIT_PCT, new_risk.take_profit_pct * 1.25), 1)
            if new_tp > new_risk.take_profit_pct:
                mutations_applied.append(
                    f"Expanded take profit from {strategy.risk_management.take_profit_pct}% to {new_tp}% "
                    f"(1:{round(new_tp / new_risk.stop_loss_pct, 1)} R:R)."
                )
                new_risk.take_profit_pct = new_tp

        if not critiques:
            critiques.append("Strategy exhibits solid metrics. Holding parameters — no forced mutation.")
            # Do NOT auto-expand target on a clean strategy: repeated runs otherwise drift target upward
            # every generation with no evidence-based reason.

        # Construct next generation version tag
        current_v = strategy.version
        try:
            major, minor, patch = map(int, current_v.split("."))
            if minor + 1 > self.MAX_GENERATIONS:
                # Cap generation counter; caller should retire the lineage after this.
                new_version = f"{major}.{self.MAX_GENERATIONS}.LOCKED"
                mutations_applied.append(f"Generation cap ({self.MAX_GENERATIONS}) reached — no further mutation.")
                new_conditions = [cond.model_copy() for cond in strategy.entry_rules.conditions]
                new_risk = strategy.risk_management.model_copy()
            else:
                new_version = f"{major}.{minor + 1}.0"
        except Exception:
            new_version = f"{current_v}-v2"

        # Safety: enforce absolute bounds on the mutated risk params.
        new_risk.stop_loss_pct = round(
            min(self.MAX_STOP_LOSS_PCT, max(self.MIN_STOP_LOSS_PCT, new_risk.stop_loss_pct)), 1
        )
        new_risk.take_profit_pct = round(min(self.MAX_TAKE_PROFIT_PCT, new_risk.take_profit_pct), 1)

        mutated_strategy = StrategyDefinition(
            strategy_id=f"{strategy.strategy_id}_MUT_{new_version.replace('.', '_')}",
            name=f"{strategy.name} (Gen {new_version})",
            description=f"Autonomous mutation of {strategy.strategy_id}. Focus: {', '.join(mutations_applied[:2])}",
            version=new_version,
            asset_universe=strategy.asset_universe,
            timeframe=strategy.timeframe,
            entry_rules=RuleGroup(
                logical_operator=strategy.entry_rules.logical_operator,
                conditions=new_conditions,
            ),
            exit_rules=strategy.exit_rules,
            risk_management=new_risk,
            position_sizing=strategy.position_sizing,
        )

        # Gate: try to re-backtest the mutation and reject it if strictly worse than the parent.
        # Only runs when the caller supplies candles; otherwise we accept the mutation but note it.
        mutation_accepted = True
        rejection_reason: Optional[str] = None
        mutated_metrics: Dict[str, Any] = {}
        if candles:
            try:
                mutated_result = self.backtest_engine.run_backtest(mutated_strategy, candles)
                mutated_metrics = mutated_result.get("metrics", {}) if isinstance(mutated_result, dict) else {}
                m_sharpe = float(mutated_metrics.get("sharpe_ratio", 0.0))
                m_dd = float(mutated_metrics.get("max_drawdown_pct", 100.0))
                if m_sharpe < sharpe - 0.1 and m_dd > max_dd + 1.0:
                    mutation_accepted = False
                    rejection_reason = (
                        f"Mutation degrades both Sharpe ({m_sharpe} vs {sharpe}) "
                        f"and drawdown ({m_dd}% vs {max_dd}%). Reverting to parent."
                    )
            except Exception as exc:
                rejection_reason = f"Re-backtest skipped: {exc}"
        else:
            rejection_reason = "Re-backtest skipped: no candles supplied."

        return {
            "parent_strategy_id": strategy.strategy_id,
            "parent_version": strategy.version,
            "mutated_strategy": mutated_strategy if mutation_accepted else strategy,
            "mutated_version": new_version if mutation_accepted else strategy.version,
            "mutation_accepted": mutation_accepted,
            "rejection_reason": rejection_reason,
            "mutated_metrics": mutated_metrics,
            "critique": critiques,
            "mutations_applied": mutations_applied,
            "timestamp": datetime.now(IST_TIMEZONE).isoformat(),
        }
