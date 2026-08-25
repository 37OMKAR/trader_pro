"""
Market AI — Quantitative Performance Metrics Calculator
Computes Sharpe, Sortino, Calmar, Max Drawdown, Win Rate, and Equity Curve statistics.
"""

import math
from typing import List, Dict, Any, Tuple
import numpy as np


class PerformanceMetricsCalculator:
    """Calculates risk-adjusted financial metrics from trade log and equity curve."""

    @staticmethod
    def calculate_metrics(
        initial_capital: float,
        equity_curve: List[Dict[str, Any]],
        trades: List[Dict[str, Any]],
        risk_free_rate: float = 0.065,  # 6.5% Indian risk-free rate
    ) -> Dict[str, Any]:
        """Calculates complete quantitative performance report."""
        if not equity_curve:
            return {}

        final_equity = equity_curve[-1]["equity"]
        total_return_pct = round(((final_equity - initial_capital) / initial_capital) * 100.0, 2)
        
        # Calculate daily returns series
        equities = [p["equity"] for p in equity_curve]
        if len(equities) > 1:
            returns = np.diff(equities) / equities[:-1]
        else:
            returns = np.array([0.0])

        # CAGR calculation (assuming 252 trading days/year)
        num_days = max(1, len(equity_curve))
        years = num_days / 252.0
        if years > 0 and final_equity > 0:
            cagr = round((((final_equity / initial_capital) ** (1.0 / years)) - 1.0) * 100.0, 2)
        else:
            cagr = total_return_pct

        # Maximum Drawdown
        peak = equities[0]
        max_dd = 0.0
        for eq in equities:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / max(peak, 1.0)
            if dd > max_dd:
                max_dd = dd
        max_drawdown_pct = round(max_dd * 100.0, 2)

        # Sharpe Ratio
        mean_ret = float(np.mean(returns)) if len(returns) > 0 else 0.0
        std_ret = float(np.std(returns)) if len(returns) > 0 else 0.0
        daily_rf = (1.0 + risk_free_rate) ** (1.0 / 252.0) - 1.0
        
        if std_ret > 0:
            sharpe = round(float((mean_ret - daily_rf) / std_ret * math.sqrt(252)), 2)
        else:
            sharpe = 0.0

        # Sortino Ratio (Downside deviation only)
        negative_returns = returns[returns < daily_rf]
        if len(negative_returns) > 0:
            downside_std = float(np.std(negative_returns))
            sortino = round(float((mean_ret - daily_rf) / max(downside_std, 1e-6) * math.sqrt(252)), 2)
        else:
            sortino = round(sharpe * 1.2, 2)

        # Calmar Ratio (CAGR / Max Drawdown)
        calmar = round(cagr / max(max_drawdown_pct, 0.01), 2)

        # Trade Statistics
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.get("pnl_inr", 0) > 0]
        losing_trades = [t for t in trades if t.get("pnl_inr", 0) < 0]
        
        win_rate = round((len(winning_trades) / max(1, total_trades)) * 100.0, 1)
        gross_profit = sum(t["pnl_inr"] for t in winning_trades)
        gross_loss = abs(sum(t["pnl_inr"] for t in losing_trades))
        profit_factor = round(gross_profit / max(1.0, gross_loss), 2)

        return {
            "initial_capital": initial_capital,
            "final_equity": round(final_equity, 2),
            "total_return_pct": total_return_pct,
            "cagr_pct": cagr,
            "max_drawdown_pct": max_drawdown_pct,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "calmar_ratio": calmar,
            "total_trades": total_trades,
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate_pct": win_rate,
            "profit_factor": profit_factor,
            "gross_profit_inr": round(gross_profit, 2),
            "gross_loss_inr": round(gross_loss, 2),
        }
