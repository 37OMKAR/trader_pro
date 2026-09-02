"""
One-cycle 'day in the life' of the autonomous Hermes firm. Synchronous and observable.

Order of operations, exactly as an unattended run would do them:
  1. Load governance + hydrate memory.
  2. For each watchlist symbol: deliberate -> PM veto -> paper order.
  3. Tick the market forward with real historical bars for 30 days.
  4. Reflect on every closed trade; update Bayesian win-prob.
  5. Nightly auditor: recalibrate analyst weights from closed trades.
  6. Print the end-of-day digest.
"""
import sys, asyncio, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ops import config as ops_config, state as ops_state
from ops.config import write_defaults
from agents.hermes_brain import HermesSupervisorBrain
from agents.execution.portfolio_manager import PortfolioManagerAgent
from agents.reflection import Reflector
from agents.llm_provider import LLMClient
from packages.market_data.yahoo_provider import YahooFinanceMarketDataProvider
from services.paper_trading.account import PaperTradingAccount
from services.auditor.calibrator import calibrate, load_weights
from services.reporting.digest import format_trade_tape, format_end_of_day


async def main():
    print("=" * 70)
    print("HERMES AUTONOMOUS FIRM — DAY IN THE LIFE")
    print("=" * 70)

    if not Path("ops/limits.json").exists():
        write_defaults()
        print(f"[OPS] Wrote default governance limits -> ops/limits.json")

    ops_state.resume()  # clear any lingering pause/halt
    cfg = ops_config.load()
    print(f"[OPS] Whitelist: {cfg.tradable_symbols[:5]}... "
          f"| Max pos {cfg.max_position_pct}% / sector {cfg.max_sector_pct}% "
          f"/ daily loss {cfg.max_daily_loss_pct}%")
    print(f"[OPS] Analyst weights in effect: {load_weights()}")

    account = PaperTradingAccount(
        account_id="HERMES_DEMO",
        name="Hermes Autonomous Fund (Demo)",
        initial_capital=1_000_000.0,
    )
    provider = YahooFinanceMarketDataProvider()
    llm = LLMClient()
    hermes = HermesSupervisorBrain()
    pm = PortfolioManagerAgent(llm)
    reflector = Reflector(llm)

    watchlist = ["RELIANCE", "TCS", "HDFCBANK"]

    # ---- 1. Deliberate + route through PM ----
    print("\n" + "-" * 70)
    print("STAGE 1 — Deliberation and Portfolio Manager veto")
    print("-" * 70)
    for symbol in watchlist:
        try:
            deliberation = await hermes.execute_supervisory_workflow(
                symbol=symbol, portfolio_value=account.get_portfolio_summary()["total_portfolio_value"],
                conduct_web_research=False,
            )
        except Exception as exc:
            print(f"  [ERR] {symbol} deliberation: {exc}")
            continue
        proposal = deliberation.get("trade_proposal", {})
        risk_eval = deliberation.get("risk_evaluation", {})
        summary = account.get_portfolio_summary()
        current_portfolio = {"cash": summary["cash_balance"],
                             "total_value": summary["total_portfolio_value"],
                             "positions": summary["positions"]}
        decision = await pm.authorize_trade(symbol, proposal, risk_eval, current_portfolio)
        action = proposal.get("action")
        net = proposal.get("net_score")
        print(f"  {symbol}: net_score={net} action={action} => PM: {decision['status']}"
              f" {decision.get('reject_code','')} {decision.get('reason','')[:60]}")
        if decision.get("trade_executed"):
            order = decision["order_details"]
            fill = account.place_order(
                symbol=order["symbol"], action=order["action"],
                quantity=int(order["quantity"]), market_price=float(order["entry_price"]),
                stop_loss=order.get("stop_loss"), target=order.get("target_1"),
            )
            if fill.get("status") == "FILLED":
                print(f"    TAPE: {format_trade_tape(fill['order'])}")

    open_positions = account.get_portfolio_summary()["positions"]
    print(f"\n  Open positions after Stage 1: {len(open_positions)}")

    # ---- 2. Tick forward with real bars ----
    print("\n" + "-" * 70)
    print("STAGE 2 — Tick engine advances 30 bars; stops/targets fire")
    print("-" * 70)
    history_by_symbol = {}
    for sym in [p["symbol"] for p in open_positions]:
        history_by_symbol[sym] = await provider.get_history(sym, timeframe="1D", limit=60)
    max_bars = min(30, max((len(c) for c in history_by_symbol.values()), default=0))
    print(f"  Ticking {max_bars} daily bars…")
    for offset in range(max_bars, 0, -1):
        bar = {}
        for sym, cs in history_by_symbol.items():
            if len(cs) < offset: continue
            c = cs[-offset]
            bar[sym] = {"high": c.high, "low": c.low, "close": c.close}
        exits = account.tick(bar)
        for ex in exits:
            ops_state.record_realized_pnl(ex["pnl"])
            ops_state.note_trade_outcome(ex["symbol"], is_win=(ex["pnl"] > 0),
                                          quarantine_after=cfg.quarantine_after_losses,
                                          quarantine_days=cfg.quarantine_days)
            print(f"    EXIT: {format_trade_tape(ex)}")
        if not account.positions:
            break

    # ---- 3. Reflect on closed trades ----
    print("\n" + "-" * 70)
    print("STAGE 3 — Reflection loop updates Bayesian win-prob")
    print("-" * 70)
    closed = [t for t in account.trade_history if t["action"] == "SELL"]
    for t in closed:
        r = await reflector.reflect_on_trade(
            symbol=t["symbol"],
            initial_thesis=f"Hermes signal-driven entry on {t['symbol']}",
            raw_return_pct=t.get("pnl_pct", 0.0), alpha_vs_nifty_pct=0.0,
            exit_reason=t.get("exit_reason", "MANUAL"),
        )
        print(f"    LESSON [{t['symbol']}]: {r['lesson'][:100]}")
    stats = Reflector.stats()
    print(f"  Reflection stats: {stats}")

    # ---- 4. Nightly auditor ----
    print("\n" + "-" * 70)
    print("STAGE 4 — Nightly auditor recalibrates analyst weights")
    print("-" * 70)
    # Feed the auditor synthetic per-analyst signal history from these closed trades.
    # (In production, this reads from the deliberation trace persisted alongside each trade.)
    audit_input = []
    for t in closed:
        audit_input.append({
            "pnl_pct": t.get("pnl_pct", 0.0),
            "analyst_signals_at_entry": {
                "fundamentals": 0.2, "technicals": 0.4,
                "sentiment": 0.1, "macro": 0.3,
            }
        })
    audit = calibrate(audit_input)
    print(f"  Sample size: {audit['sample_size']}")
    print(f"  Scores: {audit['scores']}")
    print(f"  New analyst weights: {audit['weights']}")

    # ---- 5. End-of-day digest ----
    print("\n" + "-" * 70)
    print("STAGE 5 — End-of-day digest (Telegram-ready)")
    print("-" * 70)
    print(format_end_of_day(account.get_portfolio_summary()))


if __name__ == "__main__":
    asyncio.run(main())
