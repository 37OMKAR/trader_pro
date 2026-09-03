"""
Market AI — Autonomous Trading Firm Daemon
Continuously rotates the Hermes multi-agent supervisory workflow across the Indian
large-cap universe, persisting deliberations, trades, positions, and reflections so the
Agent Activity Hub always shows fresh conversations, orders, and risk debates.
"""

import sys
import os
from pathlib import Path

WORKTREE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKTREE_ROOT))

# Load the operator's real .env keys. This worktree has no .env of its own, so
# also try the main repo checkout so we pick up OpenRouter / DeepSeek / LongCat /
# TinyFish keys the user configured there.
from dotenv import load_dotenv
load_dotenv(WORKTREE_ROOT / ".env")
_main_env = Path("D:/antigravity/sharemarkt/.env")
if _main_env.exists():
    load_dotenv(_main_env, override=False)

import asyncio
import json
import uuid
import traceback
from datetime import datetime

from apps.api.app.db.session import init_db, async_session_factory
from apps.api.app.db.models import AgentDeliberationModel
from agents.hermes_brain import HermesSupervisorBrain
from packages.market_calendar.calendar import IST_TIMEZONE

UNIVERSE = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
    "SBIN", "TATAMOTORS", "LT", "AXISBANK", "BHARTIARTL",
    "ITC", "KOTAKBANK", "HINDUNILVR", "MARUTI", "SUNPHARMA",
]

CYCLE_SLEEP_SECONDS = 45  # gap between one symbol and the next
LOOP_COOLDOWN_SECONDS = 120  # pause after finishing full universe pass


async def deliberate_and_persist(hermes: HermesSupervisorBrain, symbol: str) -> None:
    ts = datetime.now(IST_TIMEZONE).strftime("%H:%M:%S IST")
    print(f"[{ts}] >>> Hermes convening trading firm on {symbol} ...", flush=True)
    delib = await hermes.execute_supervisory_workflow(
        symbol=symbol,
        portfolio_value=1_000_000.0,
        conduct_web_research=False,
    )
    delib_id = f"DELIB-{symbol}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
    risk_committee = delib.get("risk_committee", {})
    neutral_arb = risk_committee.get("neutral_arbitration", {})

    async with async_session_factory() as session:
        row = AgentDeliberationModel(
            deliberation_id=delib_id,
            symbol=symbol,
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
        session.add(row)
        await session.commit()

    action = delib.get("trade_proposal", {}).get("action", "?")
    entry = delib.get("trade_proposal", {}).get("entry_price", 0.0)
    verdict = neutral_arb.get("consensus_summary", "n/a")[:80]
    print(
        f"    [OK] {delib_id} | Action={action} @ Rs.{entry:,.2f} | Risk Verdict: {verdict}",
        flush=True,
    )


async def main() -> None:
    print("=" * 80, flush=True)
    print(" MARKET AI — AUTONOMOUS TRADING FIRM DAEMON (Hermes Supervisor Loop)", flush=True)
    print("=" * 80, flush=True)
    await init_db()
    hermes = HermesSupervisorBrain()
    cycle = 0
    while True:
        cycle += 1
        print(f"\n============= AUTONOMOUS CYCLE #{cycle} =============", flush=True)
        for symbol in UNIVERSE:
            try:
                await deliberate_and_persist(hermes, symbol)
            except Exception as exc:
                print(f"    [ERR] {symbol}: {exc}", flush=True)
                traceback.print_exc()
            await asyncio.sleep(CYCLE_SLEEP_SECONDS)
        print(f"[cycle #{cycle} done] cooldown {LOOP_COOLDOWN_SECONDS}s before next pass ...", flush=True)
        await asyncio.sleep(LOOP_COOLDOWN_SECONDS)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[stop] Autonomous daemon halted by operator.", flush=True)
