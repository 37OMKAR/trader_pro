"""
Market AI — Hermes Multi-Agent Comprehensive Trading & Database Mapping Runner
Deploys Hermes multi-agent supervisory firm across Indian equities, executes virtual dummy money trades, backtests candidate strategies, scores tournament leaderboards, and persists all records into the database.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import os
import json
import asyncio
import uuid
from datetime import datetime, date

from apps.api.app.db.session import init_db, async_session_factory
from apps.api.app.db.models import (
    StrategyModel,
    BacktestModel,
    PaperAccountModel,
    PaperTradeModel,
    PaperPositionModel,
    AgentDeliberationModel,
    TournamentLeaderboardModel,
    ReflectionMemoryModel,
)
from packages.market_data.yahoo_provider import YahooFinanceMarketDataProvider
from packages.market_calendar.calendar import IST_TIMEZONE
from agents.hermes_brain import HermesSupervisorBrain
from agents.llm_provider import LLMClient
from services.strategy_dsl.schema import StrategyDefinition, RuleGroup, ConditionRule, RiskManagementConfig, PositionSizingConfig
from services.backtest_engine.engine import BacktestEngine
from services.paper_trading.account import PaperTradingAccount
from services.tournament_engine.tournament import StrategyTournamentEngine
from services.strategy_evolution.evolution_agent import StrategyEvolutionAgent
from agents.reflection import Reflector


async def run_hermes_comprehensive_live_trading():
    print("=" * 80)
    print("HERMES SUPERVISORY BRAIN: COMPREHENSIVE MULTI-AGENT TRADING & DB MAPPING")
    print("=" * 80)

    # 1. Initialize Database + Hydrate Reflection Memory
    print("\n[Stage 1/5] Initializing Database Schema (SQLite / PostgreSQL)...")
    await init_db()
    print("            Database tables initialized and synchronized.")

    from sqlalchemy import select as sa_select
    from agents.reflection import Reflector as _Reflector
    async with async_session_factory() as session:
        try:
            rows = (await session.execute(sa_select(ReflectionMemoryModel).order_by(ReflectionMemoryModel.created_at))).scalars().all()
            records = [
                {
                    "symbol": r.symbol,
                    "raw_return_pct": r.realized_pnl_pct,
                    "alpha_vs_nifty": r.alpha_vs_nifty,
                    "exit_reason": "PERSISTED",
                    "lesson_learned": r.lesson_learned,
                    "timestamp": r.created_at.isoformat() if r.created_at else "",
                }
                for r in rows
            ]
            loaded = _Reflector.hydrate_from_records(records)
            stats = _Reflector.stats()
            print(f"            Reflection memory hydrated: {loaded} past outcomes | global win_prob {stats['global_win_prob']}")
        except Exception as exc:
            print(f"            [WARN] Reflection hydration failed: {exc}")

    market_provider = YahooFinanceMarketDataProvider()
    hermes_brain = HermesSupervisorBrain()
    backtest_engine = BacktestEngine()
    paper_account = PaperTradingAccount(initial_capital=1_000_000.0, account_id="HERMES_PAPER_PRO_01", name="Hermes Alpha Paper Fund")
    tournament_engine = StrategyTournamentEngine()
    evolution_agent = StrategyEvolutionAgent()
    llm_client = LLMClient()
    reflector = Reflector(llm=llm_client)

    target_symbols = ["RELIANCE", "TCS", "HDFCBANK"]
    deliberations_persisted = []

    # 2. Deploy Hermes Multi-Agent Trading Firm on Indian Equities
    print("\n[Stage 2/5] Deploying Hermes Multi-Agent Trading Firm on Target Universe...")
    for sym in target_symbols:
        print(f"\n   >>> Deliberating on {sym} (4 Analysts + Bull/Bear Debate + 3-Way Risk Committee)...")
        delib = await hermes_brain.execute_supervisory_workflow(symbol=sym, portfolio_value=1_000_000.0, conduct_web_research=False)

        delib_id = f"DELIB-{sym}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
        risk_committee = delib.get("risk_committee", {})
        neutral_arb = risk_committee.get("neutral_arbitration", {})
        alloc_pct = neutral_arb.get("recommended_allocation_pct", 5.0)

        # Save to Database
        async with async_session_factory() as session:
            delib_record = AgentDeliberationModel(
                deliberation_id=delib_id,
                symbol=sym,
                horizon="5D",
                market_regime=str(delib.get("quote", {}).get("market_regime", "BULL")),
                analysts_data=json.dumps(delib.get("analyst_reports", {})),
                bullish_thesis=json.dumps(delib.get("debate", {}).get("bull_case", {})),
                bearish_thesis=json.dumps(delib.get("debate", {}).get("bear_case", {})),
                lead_trader_order=json.dumps(delib.get("trade_proposal", {})),
                risk_committee_verdict=json.dumps(neutral_arb),
                hermes_memo=str(delib.get("hermes_executive_briefing", "")),
                status="APPROVED",
                created_at=datetime.utcnow(),
            )
            session.add(delib_record)
            await session.commit()

        deliberations_persisted.append({
            "deliberation_id": delib_id,
            "symbol": sym,
            "trade_proposal": delib.get("trade_proposal", {}),
            "neutral_arbitration": neutral_arb,
            "alloc_pct": alloc_pct,
            "hermes_memo": delib.get("hermes_executive_briefing", ""),
        })
        print(f"       [DB OK] Persisted Deliberation {delib_id} | Risk Allocation: {alloc_pct}% | Allocation Reason: {neutral_arb.get('arbitration_rationale', '')[:60]}...")

    # 3. Define and Backtest Candidate Strategies
    print("\n[Stage 3/5] Defining, Backtesting & Mutating Trading Strategies...")
    
    # Strategy 1: Large-Cap Momentum V1
    strat_mom_v1 = StrategyDefinition(
        strategy_id="STRAT_MOMENTUM_V1",
        name="Large-Cap Momentum V1",
        description="20/50 DMA trend crossover with RSI momentum filter",
        version="1.0.0",
        asset_universe=target_symbols,
        timeframe="1D",
        entry_rules=RuleGroup(
            logical_operator="AND",
            conditions=[
                ConditionRule(feature="rsi_14", operator=">", threshold=52.0),
                ConditionRule(feature="close", operator=">", threshold=1000.0),
            ],
        ),
        exit_rules=RuleGroup(
            logical_operator="OR",
            conditions=[
                ConditionRule(feature="rsi_14", operator=">", threshold=78.0),
            ],
        ),
        risk_management=RiskManagementConfig(stop_loss_pct=3.5, take_profit_pct=7.5),
        position_sizing=PositionSizingConfig(sizing_type="FIXED_RISK_PCT", risk_per_trade_pct=2.0),
    )

    # Strategy 2: Mean Reversion Dip Buyer V1
    strat_mean_rev = StrategyDefinition(
        strategy_id="STRAT_MEAN_REV_V1",
        name="Mean Reversion Dip Buyer V1",
        description="Oversold RSI < 40 with lower Bollinger band bounce",
        version="1.0.0",
        asset_universe=target_symbols,
        timeframe="1D",
        entry_rules=RuleGroup(
            logical_operator="AND",
            conditions=[
                ConditionRule(feature="rsi_14", operator="<", threshold=40.0),
            ],
        ),
        exit_rules=RuleGroup(
            logical_operator="OR",
            conditions=[
                ConditionRule(feature="rsi_14", operator=">", threshold=60.0),
            ],
        ),
        risk_management=RiskManagementConfig(stop_loss_pct=4.0, take_profit_pct=8.0),
        position_sizing=PositionSizingConfig(sizing_type="FIXED_RISK_PCT", risk_per_trade_pct=2.0),
    )

    # Backtest on RELIANCE candles
    candles_rel = await market_provider.get_history("RELIANCE", limit=90)
    bt_mom_v1 = backtest_engine.run_backtest(strat_mom_v1, candles=candles_rel, initial_capital=1_000_000.0)
    bt_mean_rev = backtest_engine.run_backtest(strat_mean_rev, candles=candles_rel, initial_capital=1_000_000.0)

    # Evolve & Mutate Momentum V1 -> V2 (gated re-backtest inside).
    evo_res = evolution_agent.critique_and_evolve(strat_mom_v1, bt_mom_v1, candles=candles_rel)
    strat_mom_v2 = evo_res["mutated_strategy"]
    if not evo_res.get("mutation_accepted", True):
        print(f"       [EVOLUTION REJECTED] {evo_res.get('rejection_reason','')}")
    bt_mom_v2 = backtest_engine.run_backtest(strat_mom_v2, candles=candles_rel, initial_capital=1_000_000.0)

    strategies_to_save = [
        (strat_mom_v1, bt_mom_v1),
        (strat_mean_rev, bt_mean_rev),
        (strat_mom_v2, bt_mom_v2),
    ]

    from sqlalchemy import select

    # Save Strategies and Backtests to DB
    async with async_session_factory() as session:
        for strat, bt in strategies_to_save:
            existing = await session.scalar(select(StrategyModel).where(StrategyModel.strategy_id == strat.strategy_id))
            if not existing:
                strat_model = StrategyModel(
                    strategy_id=strat.strategy_id,
                    name=strat.name,
                    version=strat.version,
                    author_type="AGENT",
                    universe="NIFTY_50",
                    timeframe=strat.timeframe,
                    dsl_definition=json.dumps(strat.model_dump()),
                    status="ACTIVE",
                    created_at=datetime.utcnow(),
                )
                session.add(strat_model)

            bt_model = BacktestModel(
                backtest_id=bt["run_id"],
                strategy_id=strat.strategy_id,
                start_date=date.today(),
                end_date=date.today(),
                initial_capital=bt["initial_capital"],
                total_return_pct=bt["metrics"]["total_return_pct"],
                cagr_pct=bt["metrics"]["cagr_pct"],
                sharpe_ratio=bt["metrics"]["sharpe_ratio"],
                sortino_ratio=bt["metrics"]["sortino_ratio"],
                max_drawdown_pct=bt["metrics"]["max_drawdown_pct"],
                win_rate_pct=bt["metrics"]["win_rate_pct"],
                profit_factor=bt["metrics"]["profit_factor"],
                trade_count=bt["metrics"]["total_trades"],
                metrics=json.dumps(bt["metrics"]),
                created_at=datetime.utcnow(),
            )
            session.add(bt_model)
            print(f"       [DB OK] Persisted Strategy {strat.strategy_id} & Backtest {bt['run_id']} (Sharpe: {bt['metrics']['sharpe_ratio']}, MaxDD: {bt['metrics']['max_drawdown_pct']}%)")
        await session.commit()

    # Run Tournament Leaderboard & Persist to DB
    all_strats = [strat_mom_v1, strat_mean_rev, strat_mom_v2]
    tourney_res = await tournament_engine.run_tournament(strategies=all_strats, asset="RELIANCE")
    
    async with async_session_factory() as session:
        for item in tourney_res.get("leaderboard", []):
            existing_lb = await session.scalar(select(TournamentLeaderboardModel).where(TournamentLeaderboardModel.strategy_id == item["strategy_id"]))
            if not existing_lb:
                t_model = TournamentLeaderboardModel(
                    strategy_id=item["strategy_id"],
                    name=item["name"],
                    version="1.0",
                    asset="RELIANCE",
                    rank=item["rank"],
                    strategy_score=item["strategy_score"],
                    badge=item["badge"],
                    tier=item["tier"],
                    cagr_pct=item["metrics"]["cagr_pct"],
                    sharpe_ratio=item["metrics"]["sharpe_ratio"],
                    max_drawdown_pct=item["metrics"]["max_drawdown_pct"],
                    win_rate_pct=item["metrics"]["win_rate_pct"],
                    trades_count=item["trades_count"],
                    sub_scores=json.dumps(item["sub_scores"]),
                    updated_at=datetime.utcnow(),
                )
                session.add(t_model)
        await session.commit()
        await session.commit()
    print(f"       [DB OK] Persisted Tournament Leaderboard ({len(tourney_res['leaderboard'])} entries ranked).")

    # 4. Execute Virtual Dummy Money Trades and Tick the Market Forward
    print("\n[Stage 4/5] Executing Virtual Dummy Money Orders into Rs.10,00,000 Portfolio...")

    # Pull daily bars for each target: use bar[-lookahead_days] as entry, tick the rest.
    lookahead_days = 30
    history_by_symbol: Dict[str, List[Any]] = {}
    entry_prices: Dict[str, float] = {}
    for sym in target_symbols:
        candles = await market_provider.get_history(sym, timeframe="1D", limit=lookahead_days * 2 + 5)
        history_by_symbol[sym] = candles
        if len(candles) >= lookahead_days + 1:
            entry_prices[sym] = float(candles[-(lookahead_days + 1)].close)
        elif candles:
            entry_prices[sym] = float(candles[0].close)
        else:
            q = await market_provider.get_quote(sym)
            entry_prices[sym] = float(q.last_price or 2000.0)

    # Place orders at the historical entry bar. HOLDs are skipped; SELL without an existing
    # long position also skipped (short-selling not modelled in this paper account).
    for delib in deliberations_persisted:
        sym = delib["symbol"]
        order_info = delib["trade_proposal"]
        action = order_info.get("action", "HOLD")
        entry_price = entry_prices.get(sym, order_info.get("entry_price", 2500.0))
        alloc_pct = delib["alloc_pct"]

        if action == "HOLD" or alloc_pct <= 0:
            print(f"       Paper Order: HOLD {sym} @ Rs.{entry_price:,.2f} (net_score={order_info.get('net_score')})")
            continue
        if action == "SELL" and sym not in paper_account.positions:
            print(f"       Paper Order: SELL SKIPPED (no long position in {sym}); short-selling not supported.")
            continue

        trade_capital = paper_account.cash_balance * (alloc_pct / 100.0)
        qty = max(1, int(trade_capital / max(1.0, entry_price)))

        fill_res = paper_account.place_order(
            symbol=sym,
            action=action,
            quantity=qty,
            market_price=entry_price,
            stop_loss=order_info.get("stop_loss", entry_price * 0.965),
            target=order_info.get("target_1", entry_price * 1.070),
        )
        print(f"       Paper Order: {action} {qty} {sym} @ Rs.{entry_price:,.2f} -> Status: {fill_res['status']}")

    # Tick forward through the lookahead window, firing stops/targets from real OHLC.
    max_bars = min(lookahead_days, max((len(c) for c in history_by_symbol.values()), default=0))
    exits_by_symbol: Dict[str, Dict[str, Any]] = {}
    for offset in range(max_bars, 0, -1):
        bar_time = None
        bar_input: Dict[str, Dict[str, float]] = {}
        for sym, candles in history_by_symbol.items():
            if len(candles) < offset:
                continue
            c = candles[-offset]
            bar_input[sym] = {"high": c.high, "low": c.low, "close": c.close}
            bar_time = c.timestamp
        exits = paper_account.tick(bar_input, bar_time=bar_time)
        for ex in exits:
            exits_by_symbol[ex["symbol"]] = ex
        if not paper_account.positions:
            break

    # Mark-to-market surviving positions at the latest bar close.
    quotes: Dict[str, float] = {}
    for sym, candles in history_by_symbol.items():
        if candles:
            quotes[sym] = float(candles[-1].close)

    summary = paper_account.get_portfolio_summary(quotes)

    closed = sum(1 for t in paper_account.trade_history if t["action"] == "SELL")
    wins = sum(1 for t in paper_account.trade_history if t["action"] == "SELL" and t.get("pnl", 0.0) > 0)
    print(f"       Ticked {max_bars} bars | Closed {closed} of {len(target_symbols)} trades | Wins: {wins}")
    print(f"       Realized P&L: Rs.{summary['realized_pnl']:,.2f} | Unrealized P&L: Rs.{summary['unrealized_pnl']:,.2f}")

    # Persist Paper Account, Positions & Trades to DB
    async with async_session_factory() as session:
        # 1. Paper Account
        existing_acc = await session.scalar(select(PaperAccountModel).where(PaperAccountModel.account_id == paper_account.account_id))
        if existing_acc:
            existing_acc.current_cash = summary["cash_balance"]
            existing_acc.portfolio_value = summary["total_portfolio_value"]
            existing_acc.realized_pnl = summary["realized_pnl"]
            existing_acc.unrealized_pnl = summary["unrealized_pnl"]
        else:
            acc_model = PaperAccountModel(
                account_id=paper_account.account_id,
                name=paper_account.name,
                initial_balance=paper_account.initial_capital,
                current_cash=summary["cash_balance"],
                portfolio_value=summary["total_portfolio_value"],
                realized_pnl=summary["realized_pnl"],
                unrealized_pnl=summary["unrealized_pnl"],
                active=True,
                created_at=datetime.utcnow(),
            )
            session.add(acc_model)

        # 2. Paper Trades
        for trade in paper_account.trade_history:
            trade_model = PaperTradeModel(
                trade_id=trade["order_id"],
                account_id=paper_account.account_id,
                strategy_id="HERMES_MULTI_AGENT_ALPHA",
                symbol=trade["symbol"],
                side=trade["action"],
                quantity=trade["quantity"],
                price=trade["price"],
                amount=trade["price"] * trade["quantity"],
                fee=trade.get("fee", 20.0),
                order_type="MARKET",
                status="FILLED",
                executed_at=datetime.utcnow(),
            )
            session.add(trade_model)

        # 3. Paper Positions
        for pos in summary["positions"]:
            pos_model = PaperPositionModel(
                account_id=paper_account.account_id,
                symbol=pos["symbol"],
                quantity=pos["quantity"],
                average_price=pos["average_price"],
                current_price=pos["current_price"],
                invested_value=pos["invested_value"],
                current_value=pos["current_value"],
                unrealized_pnl=pos["unrealized_pnl"],
                updated_at=datetime.utcnow(),
            )
            session.add(pos_model)

        await session.commit()
    print(f"       [DB OK] Persisted Paper Account Summary, {len(paper_account.trade_history)} Trades & {len(summary['positions'])} Active Positions.")

    # 5. Post-Trade Reflection Memory Loop (only on actually-closed trades)
    print("\n[Stage 5/5] Synthesizing Post-Trade Reflection Memory Bank...")
    async with async_session_factory() as session:
        closed_trades = [t for t in paper_account.trade_history if t["action"] == "SELL"]
        if not closed_trades:
            print("       No trades closed during the tick window — nothing to reflect on.")
        for trade in closed_trades:
            raw_return_pct = float(trade.get("pnl_pct", 0.0))
            exit_reason = trade.get("exit_reason", "MANUAL_EXIT")
            entry_price = float(trade.get("entry_price", trade["price"]))
            exit_price = float(trade["price"])
            realized_pnl = float(trade.get("pnl", 0.0))
            # Alpha unknown without a NIFTY benchmark run in the same window; leave as 0.0.
            alpha_vs_nifty = 0.0

            refl = await reflector.reflect_on_trade(
                symbol=trade["symbol"],
                initial_thesis=f"Hermes multi-agent consensus trade on {trade['symbol']}",
                raw_return_pct=raw_return_pct,
                alpha_vs_nifty_pct=alpha_vs_nifty,
                exit_reason=exit_reason,
            )
            ref_model = ReflectionMemoryModel(
                reflection_id=f"REFL-{trade['order_id']}",
                trade_id=trade["order_id"],
                symbol=trade["symbol"],
                action=trade["action"],
                entry_price=entry_price,
                exit_price=exit_price,
                realized_pnl=round(realized_pnl, 2),
                realized_pnl_pct=raw_return_pct,
                alpha_vs_nifty=alpha_vs_nifty,
                lesson_learned=refl["lesson"],
                created_at=datetime.utcnow(),
            )
            session.add(ref_model)
            print(f"       [DB OK] Reflection Persisted for {trade['symbol']} | {exit_reason} {raw_return_pct:+.2f}% | Lesson: {refl['lesson'][:60]}...")
        await session.commit()

    # Final Summary Report
    print("\n" + "=" * 80)
    print("HERMES COMPREHENSIVE MULTI-AGENT TRADING & DB MAPPING: COMPLETE")
    print("=" * 80)
    print(f"Fund Account:       {paper_account.name} ({paper_account.account_id})")
    print(f"Initial Capital:    Rs.{paper_account.initial_capital:,.2f}")
    print(f"Cash Balance:       Rs.{summary['cash_balance']:,.2f}")
    print(f"Invested Value:     Rs.{summary['invested_value']:,.2f}")
    print(f"Total Portfolio:    Rs.{summary['total_portfolio_value']:,.2f}")
    print(f"Realized P&L:       Rs.{summary['realized_pnl']:,.2f}  ({summary['total_pnl_pct']:+.2f}% total)")
    closed_ct = sum(1 for t in paper_account.trade_history if t["action"] == "SELL")
    wins_ct = sum(1 for t in paper_account.trade_history if t["action"] == "SELL" and t.get("pnl", 0.0) > 0)
    win_rate = (wins_ct / closed_ct * 100.0) if closed_ct else 0.0
    print(f"Closed Trades:      {closed_ct} of {len(target_symbols)} | Wins: {wins_ct} | Win Rate: {win_rate:.1f}%")
    print(f"Active Positions:   {len(summary['positions'])} Indian Large Caps")
    print(f"Deliberations Log:  {len(deliberations_persisted)} Assets Synthesized by Hermes Super-Firm")
    print(f"Strategies Active:  3 Multi-Factor Strategies Evaluated")
    print(f"Database Mapping:   100% Persisted in SQLite / PostgreSQL (market_ai.db)")
    print("=" * 80 + "\n")


async def run_autonomous_loop(cycles: int = 3, interval_seconds: float = 0.0) -> None:
    """Run Hermes N times in sequence. Each cycle rehydrates memory so the win_prob learned
    from cycle K is used at cycle K+1. Set interval_seconds > 0 to pace the loop.
    """
    for i in range(1, cycles + 1):
        print("\n" + "#" * 80)
        print(f"HERMES AUTONOMOUS CYCLE {i}/{cycles}")
        print("#" * 80)
        await run_hermes_comprehensive_live_trading()
        if interval_seconds > 0 and i < cycles:
            await asyncio.sleep(interval_seconds)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Hermes multi-agent trading runner.")
    parser.add_argument("--cycles", type=int, default=1, help="How many supervisory cycles to run.")
    parser.add_argument("--interval", type=float, default=0.0, help="Seconds between cycles.")
    args = parser.parse_args()
    if args.cycles > 1:
        asyncio.run(run_autonomous_loop(cycles=args.cycles, interval_seconds=args.interval))
    else:
        asyncio.run(run_hermes_comprehensive_live_trading())
