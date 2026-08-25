"""
Market AI — Strategy Rule DSL Schema
Defines the strictly typed declarative Strategy DSL preventing arbitrary code execution.
"""

from typing import List, Optional, Literal, Dict, Any, Union
from pydantic import BaseModel, Field


class ConditionRule(BaseModel):
    """A single conditional comparison expression."""
    feature: str = Field(..., description="Feature indicator name (e.g. rsi_14, sma_20, last_price, volume_zscore)")
    operator: Literal[">", "<", ">=", "<=", "==", "!=", "CROSSES_ABOVE", "CROSSES_BELOW"]
    threshold: Union[float, str] = Field(..., description="Numeric constant or dynamic feature name (e.g. 30.0 or 'sma_50')")


class RuleGroup(BaseModel):
    """A group of conditions combined with boolean logic."""
    logical_operator: Literal["AND", "OR"] = "AND"
    conditions: List[ConditionRule] = Field(default_factory=list)


class RiskManagementConfig(BaseModel):
    """Risk and exit management specifications."""
    stop_loss_pct: float = Field(2.5, ge=0.1, le=20.0, description="Stop loss percentage")
    take_profit_pct: float = Field(5.0, ge=0.5, le=50.0, description="Take profit target percentage")
    trailing_stop_pct: Optional[float] = Field(None, ge=0.5, le=10.0)
    max_holding_days: int = Field(20, ge=1, le=250)


class PositionSizingConfig(BaseModel):
    """Position sizing rules."""
    sizing_type: Literal["FIXED_RISK_PCT", "FIXED_CAPITAL", "EQUAL_WEIGHT"] = "FIXED_RISK_PCT"
    risk_per_trade_pct: float = Field(1.0, ge=0.1, le=10.0)
    max_allocation_per_stock_pct: float = Field(20.0, ge=1.0, le=100.0)


class StrategyDefinition(BaseModel):
    """Complete declarative strategy specification."""
    strategy_id: str = Field(..., description="Unique slug for the strategy")
    name: str = Field(..., description="Human-readable title")
    description: str = Field(..., description="Strategy thesis description")
    version: str = Field("1.0.0", description="Semantic version tag")
    asset_universe: List[str] = Field(default_factory=lambda: ["NIFTY 50", "RELIANCE", "TCS", "HDFCBANK", "INFY"])
    timeframe: str = Field("1D", description="Base timeframe: 1m, 5m, 15m, 1h, 1D")
    
    # Entry and Exit rules
    entry_rules: RuleGroup
    exit_rules: Optional[RuleGroup] = None
    
    # Risk & Sizing
    risk_management: RiskManagementConfig = Field(default_factory=RiskManagementConfig)
    position_sizing: PositionSizingConfig = Field(default_factory=PositionSizingConfig)
