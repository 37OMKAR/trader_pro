"""
Market AI — Virtual Paper Trading Account & Portfolio State
Manages multi-strategy virtual accounts, positions, trade logs, and live mark-to-market P&L.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from packages.market_calendar.calendar import IST_TIMEZONE
from services.paper_trading.order_matcher import PaperOrderMatcher


class PaperTradingAccount:
    """Manages virtual trading account balance, open positions, and execution log."""

    def __init__(self, account_id: str = "DEFAULT_PAPER_ACC", name: str = "Master Virtual Portfolio", initial_capital: float = 1_000_000.0):
        self.account_id = account_id
        self.name = name
        self.initial_capital = float(initial_capital)
        self.cash_balance = float(initial_capital)
        self.realized_pnl = 0.0
        self.total_fees_paid = 0.0

        # Open positions: { symbol: { quantity, average_price, entry_time, stop_loss, target } }
        self.positions: Dict[str, Dict[str, Any]] = {}
        
        # Historical trade orders log
        self.trade_history: List[Dict[str, Any]] = []

    def place_order(
        self,
        symbol: str,
        action: str,  # "BUY" or "SELL"
        quantity: int,
        market_price: float,
        order_type: str = "MARKET",
        limit_price: float = 0.0,
        stop_loss: Optional[float] = None,
        target: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Places and attempts to execute a paper trading order."""
        symbol = symbol.upper().strip()
        action = action.upper().strip()
        now = datetime.now(IST_TIMEZONE)

        # 1. Handle BUY Order
        if action == "BUY":
            success, fill_price, fee, msg = PaperOrderMatcher.match_order(
                action="BUY",
                symbol=symbol,
                quantity=quantity,
                market_price=market_price,
                order_type=order_type,
                limit_price=limit_price,
            )
            if not success:
                return {"status": "REJECTED", "reason": msg}

            total_cost = (fill_price * quantity) + fee
            if self.cash_balance < total_cost:
                return {"status": "REJECTED", "reason": f"Insufficient funds: Required ₹{total_cost:,.2f}, Available ₹{self.cash_balance:,.2f}"}

            # Deduct funds
            self.cash_balance -= total_cost
            self.total_fees_paid += fee

            # Update or create position
            if symbol in self.positions:
                pos = self.positions[symbol]
                total_qty = pos["quantity"] + quantity
                total_val = (pos["quantity"] * pos["average_price"]) + (quantity * fill_price)
                pos["average_price"] = round(total_val / total_qty, 2)
                pos["quantity"] = total_qty
                pos["stop_loss"] = stop_loss or pos.get("stop_loss")
                pos["target"] = target or pos.get("target")
            else:
                self.positions[symbol] = {
                    "symbol": symbol,
                    "quantity": quantity,
                    "average_price": fill_price,
                    "entry_time": now.isoformat(),
                    "stop_loss": stop_loss or round(fill_price * 0.97, 2),
                    "target": target or round(fill_price * 1.06, 2),
                }

            order_record = {
                "order_id": f"ORD-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": now.isoformat(),
                "symbol": symbol,
                "action": "BUY",
                "quantity": quantity,
                "price": fill_price,
                "fee": fee,
                "status": "FILLED",
            }
            self.trade_history.append(order_record)
            return {"status": "FILLED", "order": order_record, "message": msg}

        # 2. Handle SELL Order
        elif action == "SELL":
            if symbol not in self.positions or self.positions[symbol]["quantity"] < quantity:
                avail = self.positions.get(symbol, {}).get("quantity", 0)
                return {"status": "REJECTED", "reason": f"Insufficient holdings: Requested to sell {quantity}, Available {avail}"}

            success, fill_price, fee, msg = PaperOrderMatcher.match_order(
                action="SELL",
                symbol=symbol,
                quantity=quantity,
                market_price=market_price,
                order_type=order_type,
                limit_price=limit_price,
            )
            if not success:
                return {"status": "REJECTED", "reason": msg}

            pos = self.positions[symbol]
            gross_proceeds = fill_price * quantity
            net_proceeds = gross_proceeds - fee
            cost_basis = pos["average_price"] * quantity

            trade_pnl = net_proceeds - cost_basis
            self.realized_pnl += trade_pnl
            self.cash_balance += net_proceeds
            self.total_fees_paid += fee

            # Reduce position
            pos["quantity"] -= quantity
            if pos["quantity"] <= 0:
                del self.positions[symbol]

            order_record = {
                "order_id": f"ORD-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": now.isoformat(),
                "symbol": symbol,
                "action": "SELL",
                "quantity": quantity,
                "price": fill_price,
                "fee": fee,
                "pnl": round(trade_pnl, 2),
                "status": "FILLED",
            }
            self.trade_history.append(order_record)
            return {"status": "FILLED", "order": order_record, "message": msg}

        return {"status": "REJECTED", "reason": "Invalid action."}

    def tick(
        self,
        bar: Dict[str, Dict[str, float]],
        bar_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Advance one price bar and fire stop-loss or target exits.

        `bar` maps symbol -> {"high": float, "low": float, "close": float}.
        Intrabar rule: if BOTH stop and target are touched in the same bar,
        assume stop hits first (conservative). Fills at the trigger price.
        Returns the list of exit trades recorded this tick.
        """
        exits: List[Dict[str, Any]] = []
        bar_time = bar_time or datetime.now(IST_TIMEZONE)
        for symbol in list(self.positions.keys()):
            candle = bar.get(symbol)
            if not candle:
                continue
            pos = self.positions[symbol]
            stop = pos.get("stop_loss")
            target = pos.get("target")
            qty = pos["quantity"]
            avg = pos["average_price"]
            high = float(candle.get("high", candle.get("close", 0.0)))
            low = float(candle.get("low", candle.get("close", 0.0)))

            fill_price: Optional[float] = None
            reason: Optional[str] = None
            if stop is not None and low <= stop:
                fill_price = float(stop)
                reason = "STOP_LOSS_HIT"
            elif target is not None and high >= target:
                fill_price = float(target)
                reason = "PROFIT_TARGET_HIT"

            if fill_price is None:
                continue

            gross_proceeds = fill_price * qty
            fee = 20.0  # flat exit slippage/fee for the simulated fill
            net_proceeds = gross_proceeds - fee
            cost_basis = avg * qty
            trade_pnl = net_proceeds - cost_basis

            self.realized_pnl += trade_pnl
            self.cash_balance += net_proceeds
            self.total_fees_paid += fee
            del self.positions[symbol]

            order_record = {
                "order_id": f"ORD-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": bar_time.isoformat(),
                "symbol": symbol,
                "action": "SELL",
                "quantity": qty,
                "price": fill_price,
                "fee": fee,
                "pnl": round(trade_pnl, 2),
                "pnl_pct": round((trade_pnl / max(1.0, cost_basis)) * 100.0, 2),
                "exit_reason": reason,
                "entry_price": avg,
                "status": "FILLED",
            }
            self.trade_history.append(order_record)
            exits.append(order_record)
        return exits

    def get_portfolio_summary(self, current_quotes: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Calculates live mark-to-market valuations and unrealized P&L."""
        current_quotes = current_quotes or {}
        invested_value = 0.0
        current_market_value = 0.0
        positions_list = []

        for symbol, pos in self.positions.items():
            qty = pos["quantity"]
            avg_price = pos["average_price"]
            ltp = current_quotes.get(symbol, avg_price)
            
            pos_invested = qty * avg_price
            pos_current = qty * ltp
            unrealized_pnl = pos_current - pos_invested
            unrealized_pnl_pct = round((unrealized_pnl / max(1.0, pos_invested)) * 100.0, 2)

            invested_value += pos_invested
            current_market_value += pos_current

            positions_list.append({
                "symbol": symbol,
                "quantity": qty,
                "average_price": avg_price,
                "current_price": ltp,
                "invested_value": round(pos_invested, 2),
                "current_value": round(pos_current, 2),
                "unrealized_pnl": round(unrealized_pnl, 2),
                "unrealized_pnl_pct": unrealized_pnl_pct,
                "stop_loss": pos.get("stop_loss"),
                "target": pos.get("target"),
                "entry_time": pos.get("entry_time"),
            })

        total_portfolio_value = self.cash_balance + current_market_value
        total_pnl = total_portfolio_value - self.initial_capital
        total_pnl_pct = round((total_pnl / self.initial_capital) * 100.0, 2)

        return {
            "account_id": self.account_id,
            "name": self.name,
            "initial_capital": self.initial_capital,
            "cash_balance": round(self.cash_balance, 2),
            "invested_value": round(invested_value, 2),
            "current_holdings_value": round(current_market_value, 2),
            "total_portfolio_value": round(total_portfolio_value, 2),
            "realized_pnl": round(self.realized_pnl, 2),
            "unrealized_pnl": round(current_market_value - invested_value, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": total_pnl_pct,
            "total_fees_paid": round(self.total_fees_paid, 2),
            "open_positions_count": len(positions_list),
            "positions": positions_list,
            "trade_history": list(reversed(self.trade_history)),
        }
