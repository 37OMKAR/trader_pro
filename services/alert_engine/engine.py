"""
Market AI — Deterministic Alert Engine
Evaluates price thresholds, RSI overbought/oversold, portfolio drawdowns, and prediction degradation rules.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from packages.market_calendar.calendar import IST_TIMEZONE


class AlertRule(BaseModel):
    rule_id: str
    symbol: str
    rule_type: str  # PRICE_ABOVE, PRICE_BELOW, RSI_OVERSOLD, RSI_OVERBOUGHT, DRAWDOWN_BREACH
    threshold: float
    message: str
    enabled: bool = True
    cooldown_minutes: int = 15
    last_triggered: Optional[str] = None


class TriggeredAlert(BaseModel):
    alert_id: str
    rule_id: str
    symbol: str
    rule_type: str
    triggered_value: float
    threshold: float
    message: str
    severity: str = "INFO"  # INFO, WARNING, CRITICAL
    timestamp: str


class AlertEngine:
    """Manages alert rules and evaluates live market conditions to trigger notifications."""

    def __init__(self):
        self._rules: List[AlertRule] = [
            AlertRule(
                rule_id="RULE_REL_HIGH",
                symbol="RELIANCE",
                rule_type="PRICE_ABOVE",
                threshold=3000.0,
                message="RELIANCE crossed above ₹3,000 psychological resistance.",
            ),
            AlertRule(
                rule_id="RULE_NIFTY_DD",
                symbol="NIFTY 50",
                rule_type="DRAWDOWN_BREACH",
                threshold=3.0,
                message="NIFTY 50 dropped more than 3% from daily high.",
            ),
            AlertRule(
                rule_id="RULE_TCS_RSI",
                symbol="TCS",
                rule_type="RSI_OVERSOLD",
                threshold=30.0,
                message="TCS 14-period RSI dipped into oversold territory (< 30).",
            ),
        ]
        self._triggered_history: List[TriggeredAlert] = [
            TriggeredAlert(
                alert_id="ALT_101",
                rule_id="RULE_TCS_RSI",
                symbol="TCS",
                rule_type="RSI_OVERSOLD",
                triggered_value=28.4,
                threshold=30.0,
                message="TCS 14-period RSI dipped into oversold territory (< 30).",
                severity="WARNING",
                timestamp=datetime.now(IST_TIMEZONE).isoformat(),
            )
        ]

    def get_rules(self) -> List[AlertRule]:
        return self._rules

    def create_rule(self, rule: AlertRule) -> AlertRule:
        self._rules.append(rule)
        return rule

    def delete_rule(self, rule_id: str) -> bool:
        initial_len = len(self._rules)
        self._rules = [r for r in self._rules if r.rule_id != rule_id]
        return len(self._rules) < initial_len

    def evaluate_tick(self, symbol: str, current_price: float, rsi: Optional[float] = None, drawdown_pct: Optional[float] = None) -> List[TriggeredAlert]:
        """Evaluates rules against a live tick."""
        new_triggers: List[TriggeredAlert] = []
        now_str = datetime.now(IST_TIMEZONE).isoformat()

        for r in self._rules:
            if not r.enabled or r.symbol.upper() != symbol.upper():
                continue

            triggered = False
            curr_val = current_price
            sev = "INFO"

            if r.rule_type == "PRICE_ABOVE" and current_price >= r.threshold:
                triggered = True
                curr_val = current_price
                sev = "INFO"
            elif r.rule_type == "PRICE_BELOW" and current_price <= r.threshold:
                triggered = True
                curr_val = current_price
                sev = "WARNING"
            elif r.rule_type == "RSI_OVERSOLD" and rsi is not None and rsi <= r.threshold:
                triggered = True
                curr_val = rsi
                sev = "WARNING"
            elif r.rule_type == "RSI_OVERBOUGHT" and rsi is not None and rsi >= r.threshold:
                triggered = True
                curr_val = rsi
                sev = "WARNING"
            elif r.rule_type == "DRAWDOWN_BREACH" and drawdown_pct is not None and drawdown_pct >= r.threshold:
                triggered = True
                curr_val = drawdown_pct
                sev = "CRITICAL"

            if triggered:
                r.last_triggered = now_str
                alert = TriggeredAlert(
                    alert_id=f"ALT_{len(self._triggered_history) + 1}",
                    rule_id=r.rule_id,
                    symbol=symbol,
                    rule_type=r.rule_type,
                    triggered_value=curr_val,
                    threshold=r.threshold,
                    message=r.message,
                    severity=sev,
                    timestamp=now_str,
                )
                self._triggered_history.append(alert)
                new_triggers.append(alert)

        return new_triggers

    def get_history(self, limit: int = 50) -> List[TriggeredAlert]:
        return self._triggered_history[-limit:]
