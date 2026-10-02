# Final Pre-Production Audit Report

**Project:** Market AI — Trader Pro
**Date:** 2026-10-02
**Reviewer:** QA engineer (session-scope)
**Verdict:** 🔴 **NOT PRODUCTION-READY** — one critical secret-leak, several high-severity architectural gaps, and multiple schema mismatches between the web client and the API must be resolved first.

---

## Verification scope

| Area | Method |
|---|---|
| API | 24 GET + 10 POST endpoint smoke test (live) |
| Web | Boot of Next.js dev server, console + network inspection, prod build |
| Agents | Code read of orchestrator + 10 agents |
| Services | Code read of all 14 services |
| DB | ORM model review |
| Tests | `pytest` 57/57 pass, `tsc --noEmit` clean, `next build` passes |
| Security | Secrets scan, CORS review, auth review, input validation review |

---

## 🔴 Critical (block release)

### C1 · Hardcoded LLM API key committed to source
**File:** `agents/llm_provider.py:26`
```python
self.longcat_key = os.getenv("LONGCAT_API_KEY") or "<REDACTED — see file>"
```
A LongCat AI API key is baked into the repository as the env fallback. The key is in the public GitHub history and must be considered compromised. The key is not reproduced in this report to avoid double-exposing it; see the source line above.

**Action required**
1. **Rotate** the LongCat key at the provider now.
2. Delete the hardcoded fallback (`or "ak_..."`) — require the env var.
3. Rewrite git history (`git filter-repo` / BFG) or make a note that the leaked key has been revoked.

### C2 · Every endpoint is unauthenticated
No `Depends(get_current_user)` or equivalent anywhere under `apps/api/`. Any browser can:
- Place / cancel paper orders (`POST /paper/orders/place`)
- Wipe the paper account (`POST /paper/account/reset`)
- Create / delete alert rules (`POST/DELETE /alerts/rules`)
- Dispatch Telegram broadcasts if a bot token is set (`POST /telegram/broadcast-alert`)

**Action required** — add an auth layer (API key header for a single-user deployment, or JWT + user table for multi-tenant) and gate all mutation endpoints behind it.

### C3 · Single global `master_account` for every user
**File:** `apps/api/app/api/endpoints/paper_trading.py:21`
```python
master_account = PaperTradingAccount(...)   # module-level singleton
```
Any viewer of the dashboard shares one account. Together with C2, this means anyone can reset or trade in anyone else's portfolio.

**Action required** — key accounts by authenticated user id and load from DB per-request.

---

## 🟠 High (fix before public launch)

### H1 · Web ↔ API schema mismatch on `strategies/backtest`
Web client payload: `{strategy, symbol, capital}`
API payload (Pydantic): `{strategy_id, name, description, entry_rules, ...}` (full `Strategy` object)
Result: Strategy Lab backtest button returns `422 Unprocessable Entity`.
Evidence: `curl -X POST /api/v1/strategies/backtest -d '{"strategy":{...},"symbol":"RELIANCE","capital":1000000}'` → `422`.

**Fix** — either extend the web client to send the full strategy object or add a thin backend wrapper that accepts `{symbol, capital}` and resolves the strategy.

### H2 · Web ↔ API schema mismatch on `evolution/evolve`
Web expects to pass `{symbol, generations}`; API requires `{strategy, backtest_result}`. Returns 422.

**Fix** — same pattern as H1.

### H3 · Web ↔ API param mismatch on `paper/account/reset`
Web sends `{initial_balance: 1_000_000}` in the body; API reads `capital` from a **query parameter**. The sent balance is silently ignored and the default 1 M is always used.
**File:** `apps/api/app/api/endpoints/paper_trading.py:148`
```python
async def reset_paper_account(capital: float = Query(1_000_000.0, ge=10000.0)):
```
**Fix** — change signature to accept a request body matching the client.

### H4 · Hardcoded `127.0.0.1:8000` URLs in production components
`apps/web/src/components/HermesSkillsView.tsx:63`
`apps/web/src/components/TalkingAvatarStudio.tsx:92`
`apps/web/src/components/TelegramConnectorModal.tsx:24,43`

These bypass the `MarketAPI` client and its `NEXT_PUBLIC_API_URL` env var — they will break in any deployment that is not the dev host.

**Fix** — route all four through `MarketAPI` methods.

### H5 · AI Predictions view fires 10 serial GETs on every tab-open
`apps/web/src/components/AIPredictionsView.tsx:22`
```tsx
const results = await Promise.all(symbols.map(sym => MarketAPI.getStockPrediction(sym, filterHorizon)));
```
Plus CORS pre-flights that doubles it to 20 HTTP calls. Will not scale beyond a small symbol list.

**Fix** — add a batch endpoint `GET /market/predictions?symbols=...&horizon=...` and call it once.

### H6 · `tutor/ask` returns a canned response regardless of question
Confirmed via `curl -X POST /tutor/ask -d '{"question":"What is a bull call spread?"}'` → always returns `"Deterministic institutional financial intelligence memo synthesized from quantitative data feeds."` with the same 3 suggested followups. The `MarketTutor` passes the prompt to the LLM, so the issue is in the `LLMClient` falling back to `_generate_local_reasoning` whenever no provider key is set.

**Fix** — either (a) remove the local-reasoning fallback and surface a clear 503 if no provider is configured, or (b) make the local fallback use the question text in its template.

---

## 🟡 Medium (plan a follow-up)

### M1 · Swallowed exceptions throughout
`except Exception: pass` or `except Exception: ...; except Exception: pass` nested patterns in:
- `apps/api/app/api/endpoints/derivatives.py:34,38`
- `apps/api/app/api/endpoints/market.py:165`
- `apps/api/app/api/endpoints/paper_trading.py:52,56,83,102,106,141`
- `apps/api/app/db/session.py:36`
- `agents/llm_provider.py:93` (silently drops individual provider errors)

These hide genuine failures (DB write failing, provider down). Replace with structured logging.

### M2 · Dev/live data provider silent fallback masks outages
When Yahoo is unavailable, `yahoo_provider` falls back to `development_provider` which generates **synthetic data**. The caller cannot tell whether a trade just executed against real quotes or against random walk data. Add a `provider` field in the response (`Quote.provider` exists but is cosmetic) and surface a UI banner when any critical path used the dev provider.

### M3 · 14-model monolithic `Base`, no migrations
`apps/api/app/db/models.py` has 14 ORM models but there is no Alembic setup — schema changes depend on `init_db()` DDL at startup. Fine for dev-SQLite; impossible for TimescaleDB in prod.

**Fix** — add Alembic and a baseline migration before switching the `DATABASE_URL`.

### M4 · WebSocket ticker has no backpressure, no auth, no origin check
`apps/api/app/main.py:132` accepts any WS connection and streams market ticks. Combined with C2, anyone can tail the live feed. Also no `max_connections` or heartbeat timeout.

### M5 · `next lint` is not wired for CI
`npm run lint:web` prompts an interactive ESLint setup, exits non-zero, breaks `npm test`. Needs a committed `.eslintrc.json` and `next lint`-to-flat-config migration.

### M6 · Fundamentals / sentiment / macro analysts still return estimated metrics
After the earlier fix for the technical analyst, the other three analysts still return deterministic sector-table + hash-jitter numbers rather than real fundamentals / news-NLP. The output is clearly labelled `data_source: "sector_profile_estimated"` but a production trading UI must not present them without that provenance badge.

### M7 · No rate limiting
Any endpoint can be hit at arbitrary RPS; the per-request CPU of `/evolution/evolve` or `/strategies/backtest` is non-trivial. Add `slowapi` or an upstream nginx/Cloudflare limit.

### M8 · WhatsApp connector is a stub
`services/notification_connectors/whatsapp_connector.py` catches all exceptions and returns success — identical structure to the pre-fix TTS stub. Either implement or remove.

---

## 🟢 Low (nice-to-have)

- **L1** — `apps/web/src/components/PaperTradingView.tsx:47` still has one `any` cast after the earlier type fix.
- **L2** — `pytest.ini` filters a legitimate `StarletteDeprecationWarning`; revisit after Starlette 0.40+.
- **L3** — `agents/analysts/sentiment_analyst.py` emits a `sentiment_score` with no provenance.
- **L4** — Several test files still use `anyio` instead of `asyncio` which can conflict with pytest-asyncio's `strict` mode in future upgrades.
- **L5** — No OpenAPI tag description or `summary` on most endpoints — Swagger UI is harder to read than it should be.
- **L6** — The web dashboard polls indices only on page load; no auto-refresh timer. Users will not see updates unless they hit the Refresh button or receive a WS tick.
- **L7** — No `/healthz` or `/readyz` endpoint. The root `/` returns a JSON payload but hits the DB implicitly through startup — fine as a liveness probe but not readiness.

---

## ✅ What works well

- **Tests**: 57/57 pass in ~70s, zero warnings, covers API + agents + 14 services + 4 packages
- **Build**: Next.js prod build succeeds, 146 KB page / 249 KB first load JS
- **Type safety**: `tsc --noEmit` clean after fixes
- **CORS**: properly scoped to `localhost:3000`, not `*`
- **Secrets scan**: no API keys found anywhere except C1
- **No raw SQL** — all queries go through SQLAlchemy ORM
- **WebSocket** `/api/v1/ws/ticker` is implemented and connects successfully
- **FastAPI docs** (`/docs`) auto-generated and complete
- **Live API**: 24/24 GET endpoints return 200 against real data
- **Multi-provider LLM fallback chain**: LongCat → OpenRouter → DeepSeek → Local
- **Agent architecture**: clean 10-agent orchestrator with clear tier boundaries

---

## Recommended release path

**Must-fix before any public endpoint:**
1. C1 (rotate + remove hardcoded key)
2. C2 (add auth)
3. H4 (hardcoded URLs in components)
4. H1 / H2 / H3 (schema mismatches — three endpoints users will exercise immediately)

**Must-fix before a multi-user deployment:**
5. C3 (per-user accounts)
6. M3 (Alembic migrations)
7. M4 (WS auth + limits)
8. M7 (rate limiting)

**Can ship with known-caveats banner for a single-user beta:**
Everything else, including the fundamentals/sentiment analyst estimation.

---

*Generated during a scheduled QA session. All findings reproduced on the running stack at `http://127.0.0.1:8000` + `http://localhost:3000`.*
