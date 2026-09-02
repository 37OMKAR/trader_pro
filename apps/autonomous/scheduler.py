"""
Autonomous scheduler — the outer loop that turns Hermes into an unattended agent.

Three coroutines run concurrently:
  1. position_tick_loop — every N seconds: mark to market, fire stops/targets. Runs even when paused.
  2. market_watch_loop  — every N seconds during market hours: check watchlist for triggers,
     enqueue deliberations.
  3. deliberation_worker — drains the queue: runs Hermes, routes through PortfolioManager,
     places the paper order.

All three respect ops.state's kill switch. State is persisted to ops/state.json.
"""

from __future__ import annotations
import asyncio
import contextlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List, Set

from ops import config as ops_config
from ops import state as ops_state
from apps.autonomous.triggers import fired
from apps.autonomous.sre_agent import SREAgent
from agents.hermes_brain import HermesSupervisorBrain
from agents.execution.portfolio_manager import PortfolioManagerAgent
from agents.execution.risk_manager import RiskManagementAgent
from agents.llm_provider import LLMClient
from agents.reflection import Reflector
from packages.market_data.yahoo_provider import YahooFinanceMarketDataProvider
from services.paper_trading.account import PaperTradingAccount

IST = timezone(timedelta(hours=5, minutes=30))


def _now_ist() -> datetime:
    return datetime.now(IST)


def _is_market_hours(now: Optional[datetime] = None) -> bool:
    """NSE cash market hours: Mon-Fri 09:15-15:30 IST."""
    now = now or _now_ist()
    if now.weekday() >= 5:
        return False
    open_t = now.replace(hour=9, minute=15, second=0, microsecond=0)
    close_t = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return open_t <= now <= close_t


class AutonomousFirm:
    """The autonomous trading firm process."""

    def __init__(
        self,
        paper_account: Optional[PaperTradingAccount] = None,
        provider: Optional[YahooFinanceMarketDataProvider] = None,
        skip_market_hours_gate: bool = False,
    ):
        self.hermes = HermesSupervisorBrain()
        self.pm = PortfolioManagerAgent(LLMClient())
        self.risk = RiskManagementAgent(LLMClient())
        self.provider = provider or YahooFinanceMarketDataProvider()
        self.account = paper_account or PaperTradingAccount(
            account_id="HERMES_AUTONOMOUS",
            name="Hermes Autonomous Fund",
            initial_capital=1_000_000.0,
        )
        self.queue: asyncio.Queue[str] = asyncio.Queue()
        self._in_flight: Set[str] = set()
        self.skip_market_hours_gate = skip_market_hours_gate
        self._stop = asyncio.Event()

    # ---------- Loops ----------

    async def position_tick_loop(self) -> None:
        cfg = ops_config.load()
        while not self._stop.is_set():
            try:
                await self._tick_positions()
                ops_state.record_tick_ok()
            except Exception as exc:
                ops_state.record_error(f"tick: {exc}")
            await asyncio.wait([asyncio.create_task(self._stop.wait())],
                               timeout=cfg.position_tick_interval_s)

    async def market_watch_loop(self) -> None:
        cfg = ops_config.load()
        while not self._stop.is_set():
            try:
                if self.skip_market_hours_gate or _is_market_hours():
                    await self._scan_watchlist(cfg)
                # else: sit quietly outside market hours; ticks still run in the other loop.
            except Exception as exc:
                ops_state.record_error(f"watch: {exc}")
            await asyncio.wait([asyncio.create_task(self._stop.wait())],
                               timeout=cfg.market_watch_interval_s)

    async def deliberation_worker(self) -> None:
        while not self._stop.is_set():
            try:
                symbol = await asyncio.wait_for(self.queue.get(), timeout=5.0)
            except asyncio.TimeoutError:
                continue
            try:
                await self._deliberate_and_act(symbol)
            except Exception as exc:
                ops_state.record_error(f"deliberate({symbol}): {exc}")
            finally:
                self._in_flight.discard(symbol)
                self.queue.task_done()

    async def run(self) -> None:
        sre = SREAgent(get_positions_count=lambda: len(self.account.positions))
        tasks = [
            asyncio.create_task(self.position_tick_loop(), name="position_tick"),
            asyncio.create_task(self.market_watch_loop(), name="market_watch"),
            asyncio.create_task(self.deliberation_worker(), name="deliberation"),
            asyncio.create_task(sre.run(self._stop), name="sre_agent"),
        ]
        try:
            await self._stop.wait()
        finally:
            for t in tasks:
                t.cancel()
            for t in tasks:
                with contextlib.suppress(BaseException):
                    await t

    def request_stop(self) -> None:
        self._stop.set()

    # ---------- Inner work ----------

    async def _scan_watchlist(self, cfg) -> None:
        watchlist = ops_state.get().watchlist or cfg.tradable_symbols
        for symbol in watchlist:
            if symbol in self._in_flight:
                continue
            if not ops_state.deliberation_allowed(symbol, cfg.deliberation_cooldown_s):
                continue
            if ops_state.is_quarantined(symbol):
                continue
            try:
                candles = await self.provider.get_history(symbol, timeframe="1D", limit=60)
            except Exception:
                continue
            trigger = fired(candles)
            if trigger:
                self._in_flight.add(symbol)
                await self.queue.put(symbol)
                # Log the trigger to state so the audit log can reconstruct it.
                ops_state.update(last_error=f"[trigger] {symbol}: {trigger}")

    async def _deliberate_and_act(self, symbol: str) -> None:
        cfg = ops_config.load()
        state = ops_state.get()

        # Budget check.
        if state.llm_calls_today >= cfg.max_llm_calls_per_day:
            ops_state.halt(f"LLM daily budget hit ({state.llm_calls_today})")
            return
        if state.errors_this_hour >= cfg.max_error_rate_per_hour:
            ops_state.halt(f"Error rate breach ({state.errors_this_hour}/hr)")
            return

        # Fresh account snapshot for PM.
        summary = self.account.get_portfolio_summary()
        current_portfolio = {
            "cash": summary["cash_balance"],
            "total_value": summary["total_portfolio_value"],
            "positions": summary["positions"],
        }

        # Hermes deliberation (many LLM calls internally; count conservatively).
        deliberation = await self.hermes.execute_supervisory_workflow(
            symbol=symbol,
            portfolio_value=current_portfolio["total_value"],
            conduct_web_research=False,
        )
        ops_state.record_llm_call(n=13)  # rough per-symbol call count; tune with metering
        ops_state.note_deliberation(symbol)

        proposal = deliberation.get("trade_proposal", {})
        risk_eval = deliberation.get("risk_evaluation", {})

        # PM gate.
        decision = await self.pm.authorize_trade(
            symbol=symbol,
            trader_proposal=proposal,
            risk_evaluation=risk_eval,
            current_portfolio=current_portfolio,
        )
        if not decision.get("trade_executed"):
            return

        order = decision["order_details"]
        entry_price = float(order["entry_price"])

        # Place the paper order.
        fill = self.account.place_order(
            symbol=order["symbol"],
            action=order["action"],
            quantity=int(order["quantity"]),
            market_price=entry_price,
            stop_loss=order.get("stop_loss"),
            target=order.get("target_1"),
        )
        ops_state.update(last_tick_ok=_now_ist().isoformat())
        # Trace hook so downstream reporting can pick this up if it wants:
        return fill

    async def _tick_positions(self) -> None:
        if not self.account.positions:
            return
        # Latest bar for each held symbol.
        bar: Dict[str, Dict[str, float]] = {}
        for symbol in list(self.account.positions.keys()):
            try:
                candles = await self.provider.get_history(symbol, timeframe="1D", limit=2)
            except Exception:
                continue
            if not candles:
                continue
            c = candles[-1]
            bar[symbol] = {"high": float(c.high), "low": float(c.low), "close": float(c.close)}
        if not bar:
            return

        cfg = ops_config.load()
        exits = self.account.tick(bar)
        for ex in exits:
            pnl = float(ex.get("pnl", 0.0))
            ops_state.record_realized_pnl(pnl)
            ops_state.note_trade_outcome(
                symbol=ex["symbol"],
                is_win=(pnl > 0),
                quarantine_after=cfg.quarantine_after_losses,
                quarantine_days=cfg.quarantine_days,
            )


async def main() -> None:
    import argparse, signal, sys
    parser = argparse.ArgumentParser(description="Hermes Autonomous Firm")
    parser.add_argument("--skip-hours-gate", action="store_true",
                        help="Watch runs continuously (dev/testing).")
    parser.add_argument("--symbols", nargs="*", help="Watchlist symbols (overrides ops.state.watchlist)")
    args = parser.parse_args()

    if args.symbols:
        ops_state.update(watchlist=[s.upper() for s in args.symbols])

    firm = AutonomousFirm(skip_market_hours_gate=args.skip_hours_gate)

    loop = asyncio.get_running_loop()
    for sig_name in ("SIGINT", "SIGTERM"):
        sig = getattr(signal, sig_name, None)
        if sig is not None:
            try:
                loop.add_signal_handler(sig, firm.request_stop)
            except NotImplementedError:
                # Windows: signal handlers not supported in loop; use default handler.
                pass

    print("[HERMES-AUTO] Starting. Kill: touch ops/state.json with halted=true.")
    await firm.run()
    print("[HERMES-AUTO] Stopped cleanly.")


if __name__ == "__main__":
    asyncio.run(main())
