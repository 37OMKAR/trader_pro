<div align="center">

# Market AI — Trader Pro

### Indian Market Autonomous Research, Prediction & Paper-Trading Platform

A production-grade monorepo that unifies live NSE/BSE market data, derivatives analytics, ML forecasting, multi-agent research, strategy evolution, paper trading, tournaments, and a Next.js dashboard — orchestrated by **Hermes**, a multi-agent brain for institutional-grade market intelligence.

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img alt="Next.js" src="https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=next.js&logoColor=white">
  <img alt="React" src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black">
  <img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-2.1-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white">
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-5.7-3178C6?style=for-the-badge&logo=typescript&logoColor=white">
</p>

<p>
  <img alt="Tests" src="https://img.shields.io/badge/tests-57%20passing-success?style=flat-square">
  <img alt="Coverage" src="https://img.shields.io/badge/coverage-integration-blue?style=flat-square">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green?style=flat-square">
  <img alt="Status" src="https://img.shields.io/badge/status-active-brightgreen?style=flat-square">
</p>

</div>

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Repository Layout](#repository-layout)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Platform](#running-the-platform)
- [API Reference](#api-reference)
- [Hermes Multi-Agent Brain](#hermes-multi-agent-brain)
- [Testing](#testing)
- [Scripts](#scripts)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**Trader Pro** is a research-first, agent-driven trading platform designed for the Indian equity and derivatives markets. It bundles everything a quantitative desk needs — data ingestion, feature engineering, ML prediction, strategy backtesting, risk management, voice/avatar briefings, and tournament-based strategy evolution — into a single, locally-runnable monorepo.

> Zero-setup execution: works out of the box with SQLite + development data providers. Flip environment variables to switch to TimescaleDB, live providers, and production voice/avatar engines.

---

## Key Features

### Market Intelligence
- Real-time **NSE/BSE** market status, indices, breadth, sectoral performance, and FII/DII flows
- Historical candles, feature extraction, and regime classification
- Corporate deep-research powered by the TinyFish web intelligence client

### Derivatives & Strategy Lab
- Black-Scholes **Greeks engine** (delta, gamma, vega, theta, rho)
- F&O universe, option chain, open interest, and IV analytics
- Natural-language strategy generator → auto-generated DSL rules
- Full strategy **backtest engine** with equity curves, Sharpe, drawdown, win-rate

### Prediction & Features
- ML prediction pipeline with persistent registry
- 100+ technical indicators via the feature engine
- Stock-level deep features and recent-prediction history

### Paper Trading & Tournaments
- Live dummy-money account summary, order placement, portfolio tracking
- Tournament leaderboards with multi-metric strategy scoring
- Strategy **evolution service** — critique, mutation, and generational improvement

### Hermes Multi-Agent Brain
- 12-skill matrix across **analysts**, **researchers**, **execution**, **risk management**, **reflection**, and **reporting**
- Pluggable LLM provider abstraction
- Autonomous research reports written to `artifacts/reports/<SYMBOL>/`

### Voice, Avatar & Notifications
- TTS briefing synthesis + talking avatar video generation
- Telegram dispatcher for alerts and daily digests
- Alert engine with rule-based tick evaluation

### Portfolio Intelligence
- VaR, stress testing, and portfolio-level risk audit

---

## Architecture

```
                                    ┌──────────────────┐
                                    │   Next.js Web    │
                                    │   Dashboard      │
                                    └────────┬─────────┘
                                             │ REST
                                             ▼
┌───────────────────────────────────────────────────────────────────────┐
│                        FastAPI Gateway (apps/api)                     │
│  market · derivatives · strategies · paper · tournaments · voice ...  │
└──────┬────────────────┬──────────────┬──────────────┬─────────────────┘
       │                │              │              │
       ▼                ▼              ▼              ▼
┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────────┐
│   Hermes    │  │  Services   │  │ Packages │  │  Database    │
│  Multi-     │  │  (14 domain │  │ (shared  │  │  SQLite /    │
│  Agent CLI  │  │  engines)   │  │  types,  │  │  TimescaleDB │
│             │  │             │  │  deriv,  │  │              │
│  12 skills  │  │             │  │  data)   │  │              │
└─────────────┘  └─────────────┘  └──────────┘  └──────────────┘
```

---

## Repository Layout

| Path | Purpose |
| :--- | :--- |
| **`apps/api`** | FastAPI backend exposing 14 REST endpoint modules |
| **`apps/web`** | Next.js 15 + React 19 dashboard with Recharts |
| **`agents`** | Hermes multi-agent orchestrator, analysts, researchers, execution, risk, reflection, reporting |
| **`services/alert_engine`** | Rule-based alert evaluation on live ticks |
| **`services/backtest_engine`** | Historical strategy simulation |
| **`services/feature_engine`** | Technical-indicator and feature pipeline |
| **`services/market_tutor`** | Educational Q&A engine |
| **`services/notification_connectors`** | Telegram, email, webhook dispatchers |
| **`services/paper_trading`** | Dummy-money account, orders, positions |
| **`services/portfolio_intelligence`** | VaR, stress tests, risk audit |
| **`services/prediction_engine`** | ML prediction generation + registry |
| **`services/regime_engine`** | Market-regime classification |
| **`services/research_agent`** | Corporate deep-research via TinyFish |
| **`services/strategy_dsl`** | Strategy rule DSL + evaluator |
| **`services/strategy_evolution`** | Critique, mutate, evolve strategies |
| **`services/tournament_engine`** | Multi-strategy scoring + leaderboards |
| **`services/voice_engine`** | TTS briefings + avatar video |
| **`packages/derivatives_engine`** | Black-Scholes, option chain, IV |
| **`packages/market_calendar`** | NSE/BSE session calendar |
| **`packages/market_data`** | Market-data providers (dev + live) |
| **`packages/shared_types`** | Pydantic domain models |

---

## Tech Stack

### Backend
- **FastAPI** `0.115` — async REST gateway
- **SQLAlchemy 2.1** — async ORM (SQLite / Timescale)
- **Pydantic** — typed domain models
- **NumPy / Pandas / SciPy** — numerics, stats, Greeks
- **yfinance / curl_cffi** — development market data

### Frontend
- **Next.js 15** + **React 19** — App Router
- **Tailwind CSS 3** — styling
- **Recharts** — financial charts
- **Lucide React** — icons

### Testing & Tooling
- **pytest** + **pytest-asyncio** — 57 integration tests
- **npm workspaces** — monorepo orchestration

---

## Prerequisites

| Tool | Version |
| :--- | :--- |
| Python | `3.11+` |
| Node.js | `18+` |
| npm | `9+` |

---

## Installation

```bash
# 1. Clone
git clone https://github.com/37OMKAR/trader_pro.git
cd trader_pro

# 2. Install JS workspaces
npm install

# 3. Install Python dependencies
python -m pip install -r apps/api/requirements.txt
```

That's it. SQLite auto-initializes on first run; development data providers return synthetic candles so you can boot the full stack with zero external credentials.

---

## Running the Platform

### Start the API

```bash
npm run dev:api
```
Launches FastAPI on `http://127.0.0.1:8000` with hot reload. Open `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

### Start the Web Dashboard

```bash
npm run dev:web
```
Launches Next.js on `http://localhost:3000`.

### Run the Hermes Agent CLI

```bash
python -m agents --symbol RELIANCE
```
Executes the full 12-skill pipeline and writes a report to `artifacts/reports/RELIANCE/`.

---

## API Reference

The FastAPI service exposes the following router groups under `apps/api/app/api/endpoints/`:

| Router | Highlights |
| :--- | :--- |
| `market` | Status, indices, breadth, FII/DII, sectors, regime |
| `derivatives` | Option chain, F&O universe, Greeks |
| `strategies` | Templates, NL-generator, backtest |
| `paper_trading` | Account, orders, positions, P&L |
| `tournaments` | Leaderboards, scoring |
| `evolution` | Strategy critique and mutation |
| `portfolio_risk` | VaR, stress tests, audit |
| `research` | Corporate deep-research |
| `alerts` | Alert rules, triggers |
| `voice` | TTS, briefings, avatar video |
| `skills` | Hermes 12-skill matrix |
| `telegram` | Dispatcher endpoints |
| `tutor` | Educational Q&A |
| `agent_activity` | Agent run history |

Full endpoint schemas are auto-documented at **`/docs`** when the API is running.

---

## Hermes Multi-Agent Brain

Hermes orchestrates a dedicated agent per cognitive role:

```
analysts     →  fundamentals · technicals · macro · sentiment
researchers  →  corporate deep-research · news intelligence
execution    →  trading plan generation
risk_mgmt    →  risk audit · exposure checks
reflection   →  self-critique · improvement loop
reporting    →  final memo synthesis
```

Each run produces a structured, versioned report:

```
artifacts/reports/<SYMBOL>/
├── 1_analysts/
│   ├── fundamentals.md
│   ├── technicals.md
│   ├── macro.md
│   └── sentiment.md
├── 2_research/
├── 3_trading/execution_plan.md
├── 4_risk/risk_audit.md
├── 5_portfolio/hermes_memo.md
└── complete_report.md
```

---

## Testing

```bash
# Full Python test suite (57 tests)
npm run test:py

# Python tests + web lint
npm test

# Target just the API integration tests
python -m pytest apps/api/tests/ -v
```

**Current status: 57/57 passing · 0 warnings · ~58s runtime.**

Coverage spans:

- API integration tests (`apps/api/tests/`) — 20 tests
- Agent reflection, orchestrator, reporting, skills — 10+ tests
- All 14 service engines
- Derivatives engine, market data providers, market calendar

---

## Scripts

| Command | Description |
| :--- | :--- |
| `npm run dev:api` | FastAPI dev server on `:8000` |
| `npm run dev:web` | Next.js dev server on `:3000` |
| `npm run build:web` | Production build of the web app |
| `npm run start:web` | Serve the built web app |
| `npm run lint:web` | ESLint over the web workspace |
| `npm run test:py` | Pytest across all configured testpaths |
| `npm test` | `test:py` + `lint:web` |

---

## Project Structure

```
trader_pro/
├── agents/                    # Hermes multi-agent brain
│   ├── analysts/
│   ├── researchers/
│   ├── execution/
│   ├── risk_mgmt/
│   ├── reflection.py
│   ├── reporting.py
│   ├── orchestrator.py
│   ├── hermes_brain.py
│   ├── llm_provider.py
│   ├── tinyfish_client.py
│   └── skills/registry.py
├── apps/
│   ├── api/                   # FastAPI backend
│   │   ├── app/
│   │   │   ├── api/endpoints/ # 14 routers
│   │   │   ├── db/            # SQLAlchemy models + session
│   │   │   └── main.py
│   │   ├── tests/
│   │   └── requirements.txt
│   └── web/                   # Next.js 15 dashboard
├── services/                  # 14 domain engines
├── packages/                  # Shared libraries
├── artifacts/reports/         # Hermes run outputs
├── pytest.ini
├── package.json               # npm workspaces root
└── README.md
```

---

## Contributing

1. Fork the repository and create a feature branch.
2. Install dependencies (`npm install && pip install -r apps/api/requirements.txt`).
3. Add tests for your change under the appropriate `tests/` folder.
4. Ensure `npm test` passes locally.
5. Open a PR with a clear description.

---

## License

Released under the **MIT License**.

---

<div align="center">

**Built for Indian markets. Designed for research-grade autonomy.**

</div>
