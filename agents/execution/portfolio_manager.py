"""
Market AI — Portfolio Manager Agent
Firm-wide gatekeeper: enforces exposure book, sector caps, daily loss budget,
kill switch and quarantines before any order reaches the paper account.

APPROVE / RESIZE / REJECT with a specific reason each time. This is the seam
that gives the risk committee real teeth — the trader's proposal is a request,
the PM answers.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from agents.llm_provider import LLMClient
from ops import config as ops_config
from ops import state as ops_state


class PortfolioManagerAgent:
    """Executive portfolio manager: enforces firm-level limits before execution."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self.name = "Portfolio Manager"

    async def authorize_trade(
        self,
        symbol: str,
        trader_proposal: Dict[str, Any],
        risk_evaluation: Dict[str, Any],
        current_portfolio: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Return {status: APPROVE|RESIZE|REJECT, quantity, reason, ...}."""
        sym = symbol.upper()
        cfg = ops_config.load()
        state = ops_state.get()
        action = trader_proposal.get("action", "HOLD")

        # 1. Hard gates — reject before any math.
        if state.halted:
            return self._reject("KILL_SWITCH_HALTED", f"Halt reason: {state.halt_reason}")
        if state.paused:
            return self._reject("KILL_SWITCH_PAUSED", state.halt_reason or "Paused by operator")
        if sym not in cfg.tradable_symbols:
            return self._reject("SYMBOL_NOT_WHITELISTED", f"{sym} not in tradable_symbols")
        if sym in state.quarantined:
            return self._reject("SYMBOL_QUARANTINED", f"Locked until {state.quarantined[sym]}")
        if action == "HOLD":
            return self._noop("HOLD", "Trader recommended HOLD; no order sent.")
        if not risk_evaluation.get("approved", False):
            return self._reject("REJECTED_BY_RISK", risk_evaluation.get("summary", "risk check failed"))

        # 2. Daily loss budget
        nav = float(current_portfolio.get("total_value", 1_000_000.0))
        if nav > 0 and (state.day_realized_pnl / nav) * 100.0 <= -abs(cfg.max_daily_loss_pct):
            ops_state.halt(f"Daily loss budget {cfg.max_daily_loss_pct}% hit "
                           f"(realized {state.day_realized_pnl:.2f})")
            return self._reject("DAILY_LOSS_BUDGET_HIT",
                                f"Realized PnL today ₹{state.day_realized_pnl:.2f} exceeds "
                                f"{cfg.max_daily_loss_pct}% of NAV. Halting.")

        # 3. Compute the proposed size and check exposure book.
        entry = float(trader_proposal["entry_price"])
        stop = float(trader_proposal["stop_loss"])
        proposed_qty = int(risk_evaluation.get("max_approved_shares", 0))
        if proposed_qty <= 0:
            return self._reject("ZERO_QUANTITY", "Risk manager approved zero shares")

        positions: List[Dict[str, Any]] = current_portfolio.get("positions", []) or []
        # Existing exposure by sector and firm-wide.
        gross_now = sum(float(p.get("current_value", 0.0)) for p in positions)
        sector_now: Dict[str, float] = {}
        for p in positions:
            s = cfg.symbol_sector.get(str(p.get("symbol", "")).upper(), "OTHER")
            sector_now[s] = sector_now.get(s, 0.0) + float(p.get("current_value", 0.0))
        sector_here = cfg.symbol_sector.get(sym, "OTHER")

        # 4. Cap per-position: max_position_pct of NAV.
        max_position_value = nav * cfg.max_position_pct / 100.0
        max_qty_position = int(max_position_value / max(1e-6, entry))

        # 5. Cap gross exposure.
        max_gross_value = nav * cfg.max_gross_exposure_pct / 100.0
        remaining_gross = max(0.0, max_gross_value - gross_now)
        max_qty_gross = int(remaining_gross / max(1e-6, entry))

        # 6. Cap sector exposure.
        max_sector_value = nav * cfg.max_sector_pct / 100.0
        remaining_sector = max(0.0, max_sector_value - sector_now.get(sector_here, 0.0))
        max_qty_sector = int(remaining_sector / max(1e-6, entry))

        # 7. Cap per-trade risk (|entry-stop| * qty / NAV).
        risk_per_share = max(1e-6, abs(entry - stop))
        max_trade_risk_value = nav * cfg.max_trade_risk_pct / 100.0
        max_qty_risk = int(max_trade_risk_value / risk_per_share)

        # 8. Cap open positions count.
        open_syms = {str(p.get("symbol", "")).upper() for p in positions}
        if sym not in open_syms and len(open_syms) >= cfg.max_open_positions:
            return self._reject("MAX_OPEN_POSITIONS",
                                f"Already at {len(open_syms)}/{cfg.max_open_positions}")

        allowed_qty = min(proposed_qty, max_qty_position, max_qty_gross, max_qty_sector, max_qty_risk)
        if allowed_qty <= 0:
            return self._reject(
                "EXPOSURE_BOOK_FULL",
                f"Caps: pos={max_qty_position} gross={max_qty_gross} "
                f"sector={max_qty_sector} risk={max_qty_risk}"
            )

        status = "APPROVE" if allowed_qty == proposed_qty else "RESIZE"
        total_cost = round(allowed_qty * entry, 2)
        cash_balance = float(current_portfolio.get("cash", nav))
        if total_cost > cash_balance:
            allowed_qty = int(cash_balance * 0.99 / entry)
            total_cost = round(allowed_qty * entry, 2)
            status = "RESIZE"
            if allowed_qty <= 0:
                return self._reject("INSUFFICIENT_CASH", f"Need ₹{total_cost:,.2f}, have ₹{cash_balance:,.2f}")

        # 9. Executive memo (LLM narrative; PM's decision above is already deterministic).
        system_prompt = (
            "You are the Chief Investment Officer. Given the deterministic PM decision below, "
            "write a 2-sentence executive memo confirming the trade parameters."
        )
        user_prompt = (
            f"{sym}: {status} — {action} {allowed_qty} @ ₹{entry} "
            f"(risk ₹{risk_per_share:.2f}/sh, sector {sector_here}, "
            f"gross_before ₹{gross_now:,.0f}, cash ₹{cash_balance:,.0f})."
        )
        try:
            llm_memo = await self.llm.generate(system_prompt, user_prompt)
        except Exception:
            llm_memo = ""

        return {
            "agent": self.name,
            "status": status,
            "trade_executed": True,
            "action": action,
            "sector": sector_here,
            "order_details": {
                "symbol": sym,
                "action": action,
                "quantity": allowed_qty,
                "entry_price": entry,
                "total_cost_inr": total_cost,
                "stop_loss": stop,
                "target_1": trader_proposal.get("target_1"),
                "target_2": trader_proposal.get("target_2"),
                "executed_at": datetime.now().isoformat(),
            },
            "caps_applied": {
                "position": max_qty_position,
                "gross": max_qty_gross,
                "sector": max_qty_sector,
                "risk": max_qty_risk,
                "requested": proposed_qty,
                "final": allowed_qty,
            },
            "portfolio_impact": {
                "previous_cash": cash_balance,
                "new_cash": round(cash_balance - total_cost, 2),
                "allocated_percentage": round((total_cost / max(1.0, nav)) * 100, 2),
                "gross_exposure_after_pct": round(((gross_now + total_cost) / max(1.0, nav)) * 100, 2),
            },
            "executive_memo": (
                f"{status}: {action} {allowed_qty} {sym} @ ₹{entry:.2f} "
                f"(₹{total_cost:,.0f}). Stop ₹{stop:.2f}, target ₹{trader_proposal.get('target_1')}."
            ),
            "llm_memo": llm_memo,
        }

    def _reject(self, code: str, reason: str) -> Dict[str, Any]:
        return {
            "agent": self.name,
            "status": "REJECT",
            "trade_executed": False,
            "reject_code": code,
            "reason": reason,
        }

    def _noop(self, code: str, reason: str) -> Dict[str, Any]:
        return {
            "agent": self.name,
            "status": "NOOP",
            "trade_executed": False,
            "reject_code": code,
            "reason": reason,
        }
