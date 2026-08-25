"""
Unit tests for Deterministic Alert Engine.
"""

from services.alert_engine.engine import AlertEngine, AlertRule


def test_alert_rule_lifecycle_and_tick_evaluation():
    engine = AlertEngine()

    rule = AlertRule(
        rule_id="RULE_INFY_BREAK",
        symbol="INFY",
        rule_type="PRICE_ABOVE",
        threshold=1900.0,
        message="INFY crossed 1900.",
    )
    engine.create_rule(rule)

    assert len(engine.get_rules()) >= 4

    # Tick below threshold -> no triggers
    triggers = engine.evaluate_tick("INFY", 1850.0)
    assert len(triggers) == 0

    # Tick above threshold -> triggers alert
    triggers = engine.evaluate_tick("INFY", 1920.0)
    assert len(triggers) == 1
    assert triggers[0].symbol == "INFY"
    assert triggers[0].triggered_value == 1920.0

    history = engine.get_history()
    assert len(history) >= 1
