# Market AI — Trader Pro

Indian Market Autonomous Research, Prediction & Paper-Trading Platform.

A multi-service monorepo covering live market data, derivatives analytics, ML predictions, backtesting, paper trading, tournaments, voice/avatar briefings, and a Next.js dashboard.

## Repository layout

| Path | Purpose |
| --- | --- |
| `apps/api` | FastAPI backend (REST endpoints for market, derivatives, strategies, paper trading, tournaments) |
| `apps/web` | Next.js dashboard |
| `agents` | Hermes multi-agent CLI (analysts, researchers, execution, risk management, reflection) |
| `services/*` | Domain engines — alerts, backtest, features, paper trading, prediction, regime, research, strategy DSL/evolution, tournaments, voice, portfolio intelligence |
| `packages/*` | Shared packages — derivatives engine, market calendar, market data providers, shared types |

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm 9+

## Setup

```bash
npm install
python -m pip install -r apps/api/requirements.txt
```

## Running

```bash
npm run dev:api
```

```bash
npm run dev:web
```

## Testing

Full Python test suite (57 tests across API, services, packages, agents):

```bash
npm run test:py
```

Web lint + Python tests:

```bash
npm test
```

## Scripts

| Command | Description |
| --- | --- |
| `npm run dev:api` | Start FastAPI on port 8000 |
| `npm run dev:web` | Start Next.js dev server |
| `npm run build:web` | Build the web app |
| `npm run start:web` | Serve the built web app |
| `npm run lint:web` | Lint the web app |
| `npm run test:py` | Run the Python test suite |

## License

MIT
