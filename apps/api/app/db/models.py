"""
Market AI — Database Schema Models (SQLAlchemy Declarative)
Supports both PostgreSQL (TimescaleDB) and SQLite for zero-setup local execution.
"""

from datetime import datetime, date
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Date,
    Boolean,
    Text,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class SymbolModel(Base):
    __tablename__ = "symbols"

    id = Column(Integer, primary_key=True, index=True)
    exchange = Column(String(10), default="NSE", nullable=False)
    symbol = Column(String(50), unique=True, index=True, nullable=False)
    isin = Column(String(50), nullable=True)
    company_name = Column(String(200), nullable=False)
    instrument_type = Column(String(20), default="EQUITY", nullable=False)
    series = Column(String(10), default="EQ")
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    lot_size = Column(Integer, default=1)
    tick_size = Column(Float, default=0.05)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CandleModel(Base):
    __tablename__ = "candles"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True, nullable=False)
    timeframe = Column(String(10), default="1D", nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, default=0)
    open_interest = Column(Integer, nullable=True)
    turnover = Column(Float, nullable=True)

    __table_args__ = (
        Index("ix_symbol_timeframe_timestamp", "symbol", "timeframe", "timestamp", unique=True),
    )


class FiiDiiModel(Base):
    __tablename__ = "fii_dii"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True, nullable=False)
    fii_buy_gross = Column(Float, nullable=False)
    fii_sell_gross = Column(Float, nullable=False)
    fii_net = Column(Float, nullable=False)
    dii_buy_gross = Column(Float, nullable=False)
    dii_sell_gross = Column(Float, nullable=False)
    dii_net = Column(Float, nullable=False)
    total_institutional_net = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class MarketBreadthModel(Base):
    __tablename__ = "breadth"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    advances = Column(Integer, nullable=False)
    declines = Column(Integer, nullable=False)
    unchanged = Column(Integer, nullable=False)
    advance_decline_ratio = Column(Float, nullable=False)
    highs_52w = Column(Integer, default=0)
    lows_52w = Column(Integer, default=0)
    upper_circuits = Column(Integer, default=0)
    lower_circuits = Column(Integer, default=0)
    total_traded_stocks = Column(Integer, nullable=False)


class MarketRegimeModel(Base):
    __tablename__ = "market_regimes"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    regime = Column(String(50), nullable=False)
    probability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    drivers = Column(JSON, nullable=True)
    risks = Column(JSON, nullable=True)


class PredictionModel(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(String(100), unique=True, index=True, nullable=False)
    symbol = Column(String(50), index=True, nullable=False)
    model_id = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    horizon = Column(String(20), nullable=False)
    direction = Column(String(20), nullable=False)
    probability = Column(Float, nullable=False)
    expected_return = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    market_regime = Column(String(50), nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    actual_return = Column(Float, nullable=True)
    actual_direction = Column(String(20), nullable=True)
    evaluated_at = Column(DateTime, nullable=True)


class StrategyModel(Base):
    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    version = Column(String(50), default="v1.0", nullable=False)
    author_type = Column(String(20), default="HUMAN", nullable=False)  # 'HUMAN' or 'AGENT'
    universe = Column(String(50), default="NIFTY_50", nullable=False)
    timeframe = Column(String(20), default="1D", nullable=False)
    dsl_definition = Column(JSON, nullable=False)
    status = Column(String(50), default="DRAFT", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class BacktestModel(Base):
    __tablename__ = "backtests"

    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(String(100), unique=True, index=True, nullable=False)
    strategy_id = Column(String(100), ForeignKey("strategies.strategy_id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    initial_capital = Column(Float, default=1_000_000.0)
    total_return_pct = Column(Float, nullable=False)
    cagr_pct = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    sortino_ratio = Column(Float, nullable=True)
    max_drawdown_pct = Column(Float, nullable=False)
    win_rate_pct = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)
    trade_count = Column(Integer, nullable=False)
    metrics = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PaperAccountModel(Base):
    __tablename__ = "paper_accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    initial_balance = Column(Float, default=1_000_000.0)
    current_cash = Column(Float, default=1_000_000.0)
    portfolio_value = Column(Float, default=1_000_000.0)
    realized_pnl = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PaperTradeModel(Base):
    __tablename__ = "paper_trades"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(String(100), unique=True, index=True, nullable=False)
    account_id = Column(String(100), ForeignKey("paper_accounts.account_id"), nullable=False)
    strategy_id = Column(String(100), nullable=True)
    symbol = Column(String(50), nullable=False)
    side = Column(String(10), nullable=False)  # BUY or SELL
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    order_type = Column(String(20), default="MARKET")
    status = Column(String(20), default="FILLED")
    executed_at = Column(DateTime, default=datetime.utcnow)
