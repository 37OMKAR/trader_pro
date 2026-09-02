# Hermes Trading — agentskills.io skill bundle

Six skills that expose the Hermes multi-agent trading brain to any agent framework
that speaks agentskills.io (e.g. Nous `hermes-agent`).

Each skill is an HTTP call against this repo's FastAPI service. Configure two env
vars in the outer agent:

- `HERMES_SKILL_BASE` — e.g. `http://localhost:8000/api/v1`
- `HERMES_SKILL_TOKEN` — bearer token; the FastAPI service reads it from the same
  var name and fails closed if it's unset.

Skills:

| File | Purpose |
|---|---|
| `deliberate.yaml` | Run full analyst → debate → trader → risk pipeline for a symbol. |
| `place_or_hold.yaml` | Route an order through the Portfolio Manager (may resize or reject). |
| `tick_and_reflect.yaml` | Advance N bars, fire stops/targets, close positions. |
| `paper_status.yaml` | NAV, positions, day P&L; optional formatted digest. |
| `evolve_strategy.yaml` | Critique + mutate a strategy, re-backtest gated. |
| `tournament.yaml` | Return the current strategy leaderboard for an asset. |
| `ops_health.yaml` | Runtime state: kill switch, budgets, quarantines. |
| `ops_pause.yaml` / `ops_resume.yaml` / `ops_halt.yaml` | Governance controls. |

## Trust boundary

Every action a skill exposes is already gated by the PortfolioManager and the
ops kill switch inside the FastAPI process. External agents cannot bypass
firm-level limits, they can only request actions.
