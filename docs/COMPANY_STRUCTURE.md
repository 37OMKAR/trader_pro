# Hermes Autonomous Trading Firm — Company Structure

> A single-process autonomous fund. Every role below is a Python module. When the
> Hermes Runner is launched, all of them come online together and stay online
> until the operator writes the stop file.

---

## The whole firm at a glance

```
                          ┌────────────────────────────┐
                          │   RUNNER  (supervisor)     │
                          │  apps/autonomous/runner.py │
                          │  keeps the scheduler alive │
                          └────────────┬───────────────┘
                                       │  spawns / restarts on crash
                                       ▼
   ┌──────────────────────────── SCHEDULER (autonomous process) ────────────────────────────┐
   │  apps/autonomous/scheduler.py                                                          │
   │                                                                                        │
   │   ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐   ┌──────────────────┐  │
   │   │ MARKET WATCH │   │ POSITION TICK│   │  DELIBERATION    │   │   SRE AGENT      │  │
   │   │  every 30s   │   │  every 10s   │   │     WORKER       │   │   every 30s      │  │
   │   │  scans TA    │   │  fires stops │   │  drains queue,   │   │  liveness,       │  │
   │   │  triggers,   │   │  & targets   │   │  runs Hermes ->  │   │  budgets,        │  │
   │   │  enqueues    │   │  on open pos │   │  PM -> paper acc │   │  auto-heal,      │  │
   │   │  symbols     │   │              │   │                  │   │  halt on stale   │  │
   │   └──────┬───────┘   └──────────────┘   └────────┬─────────┘   └────────┬─────────┘  │
   │          │                                       │                       │            │
   │          ▼                                       ▼                       ▼            │
   │      QUEUE ────────────────── deliberates ─▶ HERMES BRAIN         OPS STATE (json)   │
   └────────────────────────────────────────────────┬──────────────────────────────────────┘
                                                    │
                                                    ▼
   ┌─────────────────────── HERMES BRAIN (per-symbol pipeline) ────────────────────────────┐
   │  agents/hermes_brain.py                                                               │
   │                                                                                       │
   │   STEP 1  Analysts (parallel):  Fundamentals · Technicals · Sentiment · Macro         │
   │   STEP 2  Researchers (parallel):  Bullish · Bearish                                  │
   │   STEP 3  Lead Trader → BUY / SELL / HOLD (ATR-sized, weighted signals)               │
   │   STEP 4  Risk Committee (Aggressive · Conservative · Neutral Kelly arbiter)          │
   │   STEP 5  Executive Memo (LongCat heavy synthesis) + Portfolio Manager veto           │
   └────────────────────────────────────────┬──────────────────────────────────────────────┘
                                            │
                                            ▼
   ┌─────────────── PORTFOLIO MANAGER (gatekeeper, hard limits) ───────────────────────────┐
   │  agents/execution/portfolio_manager.py                                                │
   │  APPROVE / RESIZE / REJECT with reason code — reads ops/limits.json + ops/state.json  │
   └────────────────────────────────────────┬──────────────────────────────────────────────┘
                                            │
                                            ▼
   ┌─────────────── EXECUTION & MEMORY LAYER ──────────────────────────────────────────────┐
   │  Paper Account → Order Matcher → Trade History           (services/paper_trading/)    │
   │  Reflector → Bayesian win_prob → memory bank             (agents/reflection.py)       │
   │  Auditor (nightly) → analyst weights                     (services/auditor/)          │
   │  Reporting → digest / trade tape                         (services/reporting/)        │
   │  DB (SQLite) → PaperTradeModel, ReflectionMemoryModel    (apps/api/app/db/)           │
   └───────────────────────────────────────────────────────────────────────────────────────┘
```

Everything above runs in a single Python process. All coordination is through
two files (`ops/limits.json`, `ops/state.json`) and an in-memory `PaperTradingAccount`
kept by the scheduler.

---

## Roles (org chart)

| # | Role | Module | Cadence | Talks to |
|---|---|---|---|---|
| **Governance & Ops** | | | | |
| 1 | **Runner** (supervisor) | [apps/autonomous/runner.py](apps/autonomous/runner.py) | continuous | spawns Scheduler; reads stop file |
| 2 | **SRE Agent** (technical/debug) | [apps/autonomous/sre_agent.py](apps/autonomous/sre_agent.py) | every 30 s | reads state, writes diagnostics, can halt |
| 3 | **Governance Config** (limits) | [ops/config.py](ops/config.py) | on read | file-only, human-editable |
| 4 | **Ops State** (kill switch, budgets, counters) | [ops/state.py](ops/state.py) | per action | shared by every role |
| 5 | **Runbook / digest** | [services/reporting/digest.py](services/reporting/digest.py) | on demand | reads state + account |
| **Autonomous Runtime** | | | | |
| 6 | **Scheduler** (owns the 4 loops) | [apps/autonomous/scheduler.py](apps/autonomous/scheduler.py) | continuous | Runner ↔ Scheduler ↔ everything |
| 7 | **Market Watch loop** | [apps/autonomous/scheduler.py](apps/autonomous/scheduler.py) | every `market_watch_interval_s` (default 300 s) | Yahoo provider → Triggers → Queue |
| 8 | **Position Tick loop** | [apps/autonomous/scheduler.py](apps/autonomous/scheduler.py) | every `position_tick_interval_s` (default 60 s) | Yahoo → PaperAccount.tick |
| 9 | **Deliberation Worker** | [apps/autonomous/scheduler.py](apps/autonomous/scheduler.py) | drains queue | Hermes → PM → PaperAccount |
| 10 | **Triggers** (event detector) | [apps/autonomous/triggers.py](apps/autonomous/triggers.py) | per bar | pure functions over candles |
| **Analyst Team** | | | | |
| 11 | Fundamentals Analyst | [agents/analysts/fundamentals_analyst.py](agents/analysts/fundamentals_analyst.py) | per deliberation | reads candles, emits signal ∈ [−1, +1] |
| 12 | Technical Analyst | [agents/analysts/technical_analyst.py](agents/analysts/technical_analyst.py) | per deliberation | SMA/RSI/ATR/momentum from candles |
| 13 | Sentiment Analyst | [agents/analysts/sentiment_analyst.py](agents/analysts/sentiment_analyst.py) | per deliberation | tape proxy (volume z-score × return sign) |
| 14 | News & Macro Analyst | [agents/analysts/news_macro_analyst.py](agents/analysts/news_macro_analyst.py) | per deliberation | benchmark-index trend |
| **Debate** | | | | |
| 15 | Bullish Researcher | [agents/researchers/bullish_researcher.py](agents/researchers/bullish_researcher.py) | per deliberation | scores from analyst signals |
| 16 | Bearish Researcher | [agents/researchers/bearish_researcher.py](agents/researchers/bearish_researcher.py) | per deliberation | scores from analyst signals |
| **Trader / Risk** | | | | |
| 17 | **Lead Trader** | [agents/execution/trader_agent.py](agents/execution/trader_agent.py) | per deliberation | weighted signal → action, ATR-sized stops |
| 18 | Risk Manager | [agents/execution/risk_manager.py](agents/execution/risk_manager.py) | per deliberation | R:R, position sizing, stop distance |
| 19 | Aggressive Debator | [agents/risk_mgmt/aggressive_debator.py](agents/risk_mgmt/aggressive_debator.py) | per deliberation | argues for full Kelly |
| 20 | Conservative Debator | [agents/risk_mgmt/conservative_debator.py](agents/risk_mgmt/conservative_debator.py) | per deliberation | argues for capital preservation |
| 21 | Neutral Arbiter | [agents/risk_mgmt/neutral_debator.py](agents/risk_mgmt/neutral_debator.py) | per deliberation | Half-Kelly × VIX multiplier, learned win_prob |
| **Executive** | | | | |
| 22 | **Portfolio Manager** (veto) | [agents/execution/portfolio_manager.py](agents/execution/portfolio_manager.py) | every order | APPROVE / RESIZE / REJECT |
| 23 | Hermes Brain (CIO) | [agents/hermes_brain.py](agents/hermes_brain.py) | per deliberation | orchestrates the 5-stage flow |
| **Learning** | | | | |
| 24 | Reflector | [agents/reflection.py](agents/reflection.py) | per closed trade | Bayesian per-symbol win_prob |
| 25 | Auditor | [services/auditor/calibrator.py](services/auditor/calibrator.py) | nightly | recalibrates analyst weights |
| **Strategy R&D** | | | | |
| 26 | Strategy Evolution Agent | [services/strategy_evolution/evolution_agent.py](services/strategy_evolution/evolution_agent.py) | on demand | critiques + mutates (gated by re-backtest) |
| 27 | Tournament Engine | [services/tournament_engine/tournament.py](services/tournament_engine/tournament.py) | on demand | ranks strategies |
| 28 | Backtest Engine | [services/backtest_engine/engine.py](services/backtest_engine/engine.py) | on demand | vectorized simulation |
| **Data & Persistence** | | | | |
| 29 | Yahoo Market Data Provider | [packages/market_data/yahoo_provider.py](packages/market_data/yahoo_provider.py) | on read | live quotes, historical candles |
| 30 | Paper Trading Account | [services/paper_trading/account.py](services/paper_trading/account.py) | always | positions, cash, trade history |
| 31 | Paper Order Matcher | [services/paper_trading/order_matcher.py](services/paper_trading/order_matcher.py) | per fill | slippage + Indian fees |
| 32 | DB (SQLite / Postgres) | [apps/api/app/db/](apps/api/app/db) | writes on commit | strategies, trades, reflections |
| **Skill Surface (Nous integration)** | | | | |
| 33 | Skill HTTP Endpoints | [apps/api/app/api/endpoints/hermes_skills.py](apps/api/app/api/endpoints/hermes_skills.py) | on HTTP request | bearer-token gated |
| 34 | agentskills.io descriptors | [skills/trading/](skills/trading) | loaded by outer agent | 6 skills + 3 ops controls |
| **LLM Layer** | | | | |
| 35 | LLM Client (multi-provider) | [agents/llm_provider.py](agents/llm_provider.py) | on call | LongCat (heavy) · DeepSeek (light) · local fallback |

---

## Data & control flow (one deliberation, top to bottom)

```
  triggers.fired(candles) → scheduler enqueues symbol
        │
        ▼
  hermes.execute_supervisory_workflow(symbol)
        │
        ├── fetch: quote + 240 candles + benchmark 120 candles
        ├── hydrate: past reflections, learned win_prob, ATR, regime
        │
        ├── Analysts (asyncio.gather):
        │     fund_signal, tech_signal, sent_signal, macro_signal ∈ [-1,+1]
        │
        ├── Researchers (asyncio.gather):
        │     bull_score, bear_score ∈ [0,1]
        │
        ├── Trader:
        │     weights = ops/analyst_weights.json  (from auditor)
        │     net_score = 0.7 * Σ(w_i * s_i * c_i) + 0.3 * (bull - bear)
        │     action = BUY if net > +threshold, SELL if < -threshold, else HOLD
        │     stop  = entry ∓ (2.0 - conviction*0.8) * ATR
        │     target = entry ± 2.5 * (stop_distance)
        │
        ├── Risk Committee:
        │     Aggressive / Conservative + Kelly arbiter (win_prob from reflector)
        │
        └── Executive Memo (LongCat heavy synthesis)
              │
              ▼
        Portfolio Manager gates the order:
              hard reject if halted / paused / not whitelisted / quarantined
              resize if over position / sector / gross / trade-risk / cash caps
              hard halt if daily loss budget breached
              APPROVE → account.place_order(...)
                              │
                              ▼
                       PaperOrderMatcher fills at market ± slippage, deducts Indian fees
                              │
                              ▼
                       Position now live; TICK LOOP monitors OHLC each bar:
                          low ≤ stop  → SELL at stop  (STOP_LOSS_HIT)
                          high ≥ target → SELL at target (PROFIT_TARGET_HIT)
                              │
                              ▼
                       On exit: Reflector.reflect_on_trade → update Bayesian win_prob
                                ops_state.note_trade_outcome → maybe quarantine
                                ops_state.record_realized_pnl → maybe daily-loss halt
```

---

## Layering (what depends on what)

```
Layer 6 — Interfaces          hermes_skills endpoints    skills/trading/*.yaml
                              ┃                           ┃
Layer 5 — Reporting          services/reporting/digest.py
                              ┃
Layer 4 — Learning           services/auditor/calibrator.py    agents/reflection.py
                              ┃                                 ┃
Layer 3 — Autonomy runtime   apps/autonomous/{scheduler,runner,sre_agent,triggers}.py
                              ┃
Layer 2 — Agents             agents/{hermes_brain,execution,analysts,researchers,risk_mgmt}
                              ┃
Layer 1 — Services           paper_trading    backtest_engine    strategy_evolution    tournament_engine
                              ┃
Layer 0 — Foundation         ops/{config,state}   packages/market_data   agents/{indicators,llm_provider}   apps/api/app/db
```

An upper layer imports lower ones; lower layers never import up.

---

## Governance & kill switch (the "corporate policy")

| File | Purpose | Who writes |
|---|---|---|
| `ops/limits.json` | Hard caps: whitelist, position/sector/gross %, daily loss %, LLM budgets, cadences, quarantine thresholds. | **Human only.** Agents never write. |
| `ops/state.json` | Runtime state: paused/halted flags, budgets consumed, quarantines, per-symbol cooldowns, last tick timestamp, last SRE diagnostic. | Any role via `ops.state.*` helpers; SRE + PM are the frequent writers. |
| `ops/runner.stop` | Presence of file tells Runner to exit after current child. | Human only. |
| `ops/analyst_weights.json` | Weights the trader uses to combine analyst signals. Auto-written by the nightly Auditor. | Auditor writes; trader reads. |

**Three levels of stop:**

1. **`paused=True`** — new orders refused, position tick still protects open stops.
2. **`halted=True`** — same as pause + no auto-resume. Manual reset only.
3. **`ops/runner.stop` exists** — Runner exits after child. Full shutdown.

Any of the four coroutines can call `ops_state.halt(reason)`. The PM halts on
daily-loss breach. The SRE halts on stale tick, error spike, LLM budget breach.
The Runner never trades — it only spawns.

---

## Runbook

### Start non-stop
```bash
python -m apps.autonomous.runner --skip-hours-gate --symbols RELIANCE TCS HDFCBANK INFY
```
Runner spawns Scheduler. Scheduler starts 4 coroutines (market watch, position
tick, deliberation worker, SRE agent). Runs until you write the stop file.

### Full stop
```bash
touch ops/runner.stop      # runner exits after current scheduler child
# OR: kill the runner process; it will forward SIGTERM to the child.
```

### Pause new orders (open stops still protected)
```bash
python -c "from ops import state; state.pause('operator review')"
```

### Hard halt (manual resume required)
```bash
python -c "from ops import state; state.halt('incident')"
```

### Resume
```bash
python -c "from ops import state; state.resume()"
rm -f ops/runner.stop
```

### Live health
```bash
cat ops/state.json | python -m json.tool
```
Key fields: `paused`, `halted`, `halt_reason`, `last_tick_ok` (should be < 3× tick
interval), `errors_this_hour`, `llm_calls_today`, `quarantined`, `last_diagnostic`
(JSON of the last SRE check).

### Change limits without restarting
Edit `ops/limits.json` — every role re-reads it on each cycle.

### Nightly digest to console (paste into Telegram / Slack)
```bash
python -c "
from services.paper_trading.account import PaperTradingAccount
from services.reporting.digest import format_end_of_day
a = PaperTradingAccount(account_id='HERMES_AUTONOMOUS')
print(format_end_of_day(a.get_portfolio_summary()))
"
```

### Reset all quarantines / consecutive losses / daily P&L
```bash
python -c "
from ops import state
s = state.get()
s.quarantined = {}
s.consecutive_losses = {}
s.day_realized_pnl = 0.0
state.update(quarantined=s.quarantined, consecutive_losses=s.consecutive_losses,
             day_realized_pnl=s.day_realized_pnl)
"
```

---

## Reliability contract

- The **Position Tick loop runs even when paused**. It's the deterministic circuit
  that protects your capital when the LLM is down, the network is flaky, or the
  operator is asleep. It uses no LLM and only cheap Yahoo calls.
- The **Portfolio Manager is deterministic**. Its decisions never depend on LLM
  output. LLM memo is written after the decision, not before.
- The **SRE Agent uses no LLM and no external I/O**. Its job is to keep the
  process healthy; it must never itself be a source of failure.
- The **Runner is a plain Python subprocess supervisor**. No web deps, no LLM.
  If it crashes, systemd (or your process manager of choice) should restart it.
- Any role can write to `ops/state.json` via the `ops.state.*` helpers. Writes
  are atomic (tmp file + rename). Reads happen at the top of every cycle.

---

## Where LLM calls actually happen (updated to your `.env`)

| Where | force | heavy | Provider (with current `.env`) |
|---|---|---|---|
| Analysts (all four) | no | no | **skipped** (`USE_LLM_COMMENTARY=0`) → local synthesizer |
| Researchers (bull, bear) | no | no | skipped |
| Trader rationale | no | no | skipped |
| Risk Committee agents | no | no | skipped |
| **Hermes executive memo** | **yes** | **yes** | **LongCat-2.0** (heavy) |
| **Reflector lesson** | **yes** | **yes** | **LongCat-2.0** (heavy) |
| Fallback for heavy calls if LongCat down | — | — | DeepSeek |

Total LLM cost per deliberation ≈ **1 LongCat call** (executive memo). Per
closed trade ≈ **1 LongCat call** (reflection). Everything else runs at
compute speed.

---

## Persistence model

- **`ops/state.json`** — mutable runtime facts. Rewritten atomically per action.
- **`ops/limits.json`** — corporate policy. Human-only. Re-read on every cycle.
- **`ops/analyst_weights.json`** — auditor output. Rewritten only when sample ≥ 10.
- **SQLite DB** (`apps/api/app/db/`) — durable audit trail. `PaperTradeModel`,
  `PaperPositionModel`, `PaperAccountModel`, `ReflectionMemoryModel`,
  `StrategyModel`, `BacktestModel`, `TournamentLeaderboardModel`,
  `AgentDeliberationModel`. Everything the reflector needs on next startup is
  hydrated from here.

Restart the process → memory bank re-hydrates from the DB → learned win_prob
resumes exactly where it left off. There is no in-memory-only state that matters.
