"""
Market AI — High-Performance Quantitative Backtest Engine
Simulates realistic trade execution with Indian transaction cost structure,
slippage modeling, stop-loss enforcement, and equity curve tracking.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from packages.shared_types.market_types import Candle, Quote
from services.strategy_dsl.schema import StrategyDefinition
from services.strategy_dsl.evaluator import DSLEvaluator
from services.feature_engine.pipeline import FeaturePipeline
from services.backtest_engine.metrics import PerformanceMetricsCalculator


class BacktestEngine:
    """Executes backtests on historical candlestick data using declarative Strategy DSL."""

    def __init__(self):
        self.feature_pipeline = FeaturePipeline()
        self.metrics_calc = PerformanceMetricsCalculator()

    @staticmethod
    def calculate_indian_transaction_cost(traded_value: float, is_buy: bool = True) -> float:
        """
        Computes accurate Indian regulatory and broker transaction costs:
        - Brokerage: min(20.0, 0.0003 * traded_value)
        - STT: 0.1% on delivery
        - Exchange turnover fee: 0.00345%
        - GST: 18% on (brokerage + turnover fee)
        - Stamp duty: 0.015% on buys
        """
        brokerage = min(20.0, 0.0003 * traded_value)
        stt = 0.001 * traded_value
        turnover_fee = 0.0000345 * traded_value
        gst = 0.18 * (brokerage + turnover_fee)
        stamp_duty = (0.00015 * traded_value) if is_buy else 0.0

        total_tax = brokerage + stt + turnover_fee + gst + stamp_duty
        return round(float(total_tax), 2)

    def run_backtest(
        self,
        strategy: StrategyDefinition,
        candles: List[Candle],
        initial_capital: float = 1_000_000.0,
        slippage_pct: float = 0.05,  # 0.05% slippage
    ) -> Dict[str, Any]:
        """Runs vectorized/event simulation across candles."""
        if len(candles) < 25:
            raise ValueError("Insufficient candle history for backtesting (minimum 25 candles required).")

        run_id = f"BT-{strategy.strategy_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
        cash = initial_capital
        position_shares = 0
        entry_price = 0.0
        entry_time = None
        entry_cost = 0.0

        trades: List[Dict[str, Any]] = []
        equity_curve: List[Dict[str, Any]] = []

        stop_loss_pct = strategy.risk_management.stop_loss_pct / 100.0
        take_profit_pct = strategy.risk_management.take_profit_pct / 100.0

        for i in range(21, len(candles)):
            current_candle = candles[i]
            history_slice = candles[: i + 1]
            close_price = current_candle.close

            # Create dynamic mock quote and feature dict
            prev_close = candles[i - 1].close if i > 0 else close_price
            price_diff = close_price - prev_close
            quote = Quote(
                symbol=strategy.strategy_id,
                last_price=close_price,
                open=current_candle.open,
                high=current_candle.high,
                low=current_candle.low,
                previous_close=prev_close,
                change=round(price_diff, 2),
                percent_change=round((price_diff / max(0.01, prev_close)) * 100, 2),
                volume=current_candle.volume,
                timestamp=current_candle.timestamp,
            )
            features = self.feature_pipeline.extract_features(
                symbol=strategy.strategy_id,
                quote=quote,
                candles=history_slice,
            )
            # Flatten features for DSL evaluator
            flat_features = {
                **features["price_features"],
                **features["volume_features"],
                **features["fundamental_features"],
                "close": close_price,
                "volume": current_candle.volume,
            }

            # 1. Check Exit for open position
            if position_shares > 0:
                pnl_pct = (close_price - entry_price) / entry_price
                is_stop_loss = pnl_pct <= -stop_loss_pct
                is_take_profit = pnl_pct >= take_profit_pct
                dsl_exit = DSLEvaluator.should_exit_trade(strategy, flat_features)

                if is_stop_loss or is_take_profit or dsl_exit:
                    # Execute Exit with slippage
                    fill_price = close_price * (1.0 - (slippage_pct / 100.0))
                    gross_proceeds = position_shares * fill_price
                    exit_cost = self.calculate_indian_transaction_cost(gross_proceeds, is_buy=False)
                    net_proceeds = gross_proceeds - exit_cost
                    cash += net_proceeds

                    trade_pnl = net_proceeds - (position_shares * entry_price + entry_cost)
                    trade_pnl_pct = round((trade_pnl / (position_shares * entry_price)) * 100.0, 2)

                    trades.append({
                        "entry_time": entry_time.isoformat() if hasattr(entry_time, "isoformat") else str(entry_time),
                        "exit_time": current_candle.timestamp.isoformat(),
                        "entry_price": round(entry_price, 2),
                        "exit_price": round(fill_price, 2),
                        "shares": position_shares,
                        "pnl_inr": round(trade_pnl, 2),
                        "pnl_pct": trade_pnl_pct,
                        "exit_reason": "STOP_LOSS" if is_stop_loss else ("TAKE_PROFIT" if is_take_profit else "SIGNAL_EXIT"),
                        "total_fees_inr": round(entry_cost + exit_cost, 2),
                    })

                    position_shares = 0
                    entry_price = 0.0
                    entry_cost = 0.0

            # 2. Check Entry if no position open
            elif position_shares == 0:
                if DSLEvaluator.should_enter_trade(strategy, flat_features):
                    # Sizing: e.g. 15% of portfolio
                    alloc_capital = cash * (strategy.position_sizing.max_allocation_per_stock_pct / 100.0)
                    fill_price = close_price * (1.0 + (slippage_pct / 100.0))
                    shares_to_buy = int(alloc_capital // fill_price)

                    if shares_to_buy > 0:
                        buy_val = shares_to_buy * fill_price
                        entry_cost = self.calculate_indian_transaction_cost(buy_val, is_buy=True)
                        total_cost = buy_val + entry_cost

                        if cash >= total_cost:
                            cash -= total_cost
                            position_shares = shares_to_buy
                            entry_price = fill_price
                            entry_time = current_candle.timestamp

            # Track daily equity
            current_equity = cash + (position_shares * close_price)
            equity_curve.append({
                "timestamp": current_candle.timestamp.isoformat(),
                "equity": round(current_equity, 2),
                "cash": round(cash, 2),
                "drawdown_pct": 0.0,  # Will be normalized by metrics
            })

        # Calculate final metrics
        metrics = self.metrics_calc.calculate_metrics(initial_capital, equity_curve, trades)

        return {
            "run_id": run_id,
            "strategy_id": strategy.strategy_id,
            "strategy_name": strategy.name,
            "asset": strategy.asset_universe[0] if strategy.asset_universe else "NIFTY 50",
            "timeframe": strategy.timeframe,
            "start_date": candles[0].timestamp.isoformat() if candles else None,
            "end_date": candles[-1].timestamp.isoformat() if candles else None,
            "initial_capital": initial_capital,
            "metrics": metrics,
            "trades": trades,
            "equity_curve": equity_curve,
        }
