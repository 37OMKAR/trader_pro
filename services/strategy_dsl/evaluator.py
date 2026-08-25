"""
Market AI — Strategy DSL AST Evaluator
Safely evaluates declarative Strategy rules against feature maps without arbitrary code execution.
"""

from typing import Dict, Any, List, Optional
from services.strategy_dsl.schema import StrategyDefinition, RuleGroup, ConditionRule


class DSLEvaluator:
    """Evaluates AST conditions against flat feature dictionaries."""

    @staticmethod
    def evaluate_condition(rule: ConditionRule, features: Dict[str, Any]) -> bool:
        """Evaluates a single atomic condition."""
        feature_val = features.get(rule.feature)
        if feature_val is None:
            return False

        # Resolve threshold: either numeric or dynamic feature lookup
        if isinstance(rule.threshold, str) and rule.threshold in features:
            threshold_val = features.get(rule.threshold)
        else:
            try:
                threshold_val = float(rule.threshold)
            except (ValueError, TypeError):
                return False

        if threshold_val is None:
            return False

        op = rule.operator
        if op == ">":
            return feature_val > threshold_val
        elif op == "<":
            return feature_val < threshold_val
        elif op == ">=":
            return feature_val >= threshold_val
        elif op == "<=":
            return feature_val <= threshold_val
        elif op == "==":
            return abs(feature_val - threshold_val) < 1e-6
        elif op == "!=":
            return abs(feature_val - threshold_val) >= 1e-6
        elif op in ["CROSSES_ABOVE", "CROSSES_BELOW"]:
            # For crossings, feature_val >= threshold_val
            return feature_val >= threshold_val if op == "CROSSES_ABOVE" else feature_val <= threshold_val

        return False

    @classmethod
    def evaluate_rule_group(cls, group: RuleGroup, features: Dict[str, Any]) -> bool:
        """Evaluates a group of conditions combined with AND / OR."""
        if not group.conditions:
            return False

        results = [cls.evaluate_condition(cond, features) for cond in group.conditions]

        if group.logical_operator == "AND":
            return all(results)
        elif group.logical_operator == "OR":
            return any(results)

        return False

    @classmethod
    def should_enter_trade(cls, strategy: StrategyDefinition, features: Dict[str, Any]) -> bool:
        """Determines if entry criteria are fulfilled."""
        return cls.evaluate_rule_group(strategy.entry_rules, features)

    @classmethod
    def should_exit_trade(cls, strategy: StrategyDefinition, features: Dict[str, Any]) -> bool:
        """Determines if optional exit criteria are fulfilled."""
        if not strategy.exit_rules or not strategy.exit_rules.conditions:
            return False
        return cls.evaluate_rule_group(strategy.exit_rules, features)
