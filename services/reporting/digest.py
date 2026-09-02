"""
End-of-day and per-fill formatters. Return plain-text messages that any connector
(Telegram, Slack, stdout) can send verbatim. No side effects.
"""

from typing import Dict, Any, List
from datetime import datetime
from ops import state as ops_state


def format_trade_tape(trade: Dict[str, Any]) -> str:
    """One-line for a single fill (BUY or SELL)."""
    ts = trade.get("timestamp", "")[:19]
    sym = trade.get("symbol", "?")
    action = trade.get("action", "?")
    qty = trade.get("quantity", 0)
    price = trade.get("price", 0.0)
    line = f"[{ts}] {action:4} {qty:>5} {sym:<10} @ ₹{price:>10,.2f}"
    if action == "SELL":
        pnl = trade.get("pnl", 0.0)
        pct = trade.get("pnl_pct", 0.0)
        reason = trade.get("exit_reason", "")
        line += f"  PnL ₹{pnl:+,.2f} ({pct:+.2f}%) [{reason}]"
    return line


def format_end_of_day(
    account_summary: Dict[str, Any],
    benchmark_return_pct: float = 0.0,
) -> str:
    """Human-readable EoD digest string."""
    s = account_summary
    positions: List[Dict[str, Any]] = s.get("positions", [])
    trades: List[Dict[str, Any]] = s.get("trade_history", []) or []
    today = datetime.utcnow().date().isoformat()

    # Today's trades
    todays = [t for t in trades if str(t.get("timestamp", ""))[:10] == today]
    entries = [t for t in todays if t["action"] == "BUY"]
    exits = [t for t in todays if t["action"] == "SELL"]

    biggest_win = max((t for t in exits if t.get("pnl", 0) > 0), key=lambda t: t["pnl"], default=None)
    biggest_loss = min((t for t in exits if t.get("pnl", 0) < 0), key=lambda t: t["pnl"], default=None)

    ops = ops_state.get()
    lines = [
        "=" * 60,
        f"HERMES END-OF-DAY DIGEST — {today}",
        "=" * 60,
        f"NAV: ₹{s.get('total_portfolio_value', 0):,.2f}   "
        f"(Cash ₹{s.get('cash_balance', 0):,.2f})",
        f"Day realized P&L: ₹{ops.day_realized_pnl:+,.2f}",
        f"Unrealized P&L:   ₹{s.get('unrealized_pnl', 0):+,.2f}",
        f"Total P&L vs init: ₹{s.get('total_pnl', 0):+,.2f} ({s.get('total_pnl_pct', 0):+.2f}%)",
        f"Alpha vs benchmark: {(s.get('total_pnl_pct', 0) - benchmark_return_pct):+.2f}%",
        "",
        f"Trades today: {len(todays)}  (Entries: {len(entries)}  Exits: {len(exits)})",
    ]
    if biggest_win:
        lines.append(
            f"Biggest win:  {biggest_win['symbol']} +₹{biggest_win['pnl']:,.2f} "
            f"({biggest_win.get('pnl_pct', 0):+.2f}%)"
        )
    if biggest_loss:
        lines.append(
            f"Biggest loss: {biggest_loss['symbol']} ₹{biggest_loss['pnl']:+,.2f} "
            f"({biggest_loss.get('pnl_pct', 0):+.2f}%)"
        )
    lines += [
        "",
        f"Open positions: {len(positions)}",
    ]
    for p in positions[:10]:
        lines.append(
            f"  {p['symbol']:<10}  {p['quantity']:>4} @ ₹{p['average_price']:>10,.2f}  "
            f"MTM ₹{p['current_value']:>12,.2f}  ({p.get('unrealized_pnl_pct', 0):+.2f}%)"
        )
    lines += [
        "",
        f"LLM calls today: {ops.llm_calls_today}",
        f"Errors this hour: {ops.errors_this_hour}",
        f"Kill switch: paused={ops.paused} halted={ops.halted}"
        + (f" ({ops.halt_reason})" if ops.halt_reason else ""),
        f"Quarantined: {', '.join(sorted(ops.quarantined.keys())) or '(none)'}",
        "=" * 60,
    ]
    return "\n".join(lines)


def format_weekly_review(
    account_summary: Dict[str, Any],
    reflection_stats: Dict[str, Any],
) -> str:
    """Weekly performance + learning snapshot."""
    s = account_summary
    r = reflection_stats
    lines = [
        "=" * 60,
        f"HERMES WEEKLY REVIEW — {datetime.utcnow().date().isoformat()}",
        "=" * 60,
        f"NAV: ₹{s.get('total_portfolio_value', 0):,.2f}  "
        f"(Total P&L {s.get('total_pnl_pct', 0):+.2f}%)",
        f"Trades recorded: {r.get('trades_recorded', 0)}  "
        f"Wins {r.get('wins', 0)} / Losses {r.get('losses', 0)}",
        f"Global win probability (Bayesian): {r.get('global_win_prob', 0.5)}",
        "=" * 60,
    ]
    return "\n".join(lines)
