# Market AI — Institutional Platform Makefile

.PHONY: help dev test test-fast backtest paper agent acceptance health migrate build docker-up docker-down

help:
	@echo "Market AI — Available Commands:"
	@echo "  make dev          Start API backend and Next.js frontend"
	@echo "  make test         Run full test suite (55+ tests)"
	@echo "  make backtest     Run Strategy Backtest CLI"
	@echo "  make paper        Run Paper Trading Account CLI"
	@echo "  make agent        Run Hermes Multi-Agent Trading Firm CLI"
	@echo "  make acceptance   Run Section 107 Autonomous Strategy Acceptance Test"
	@echo "  make health       Run Section 109 Definition of Done Platform Audit"
	@echo "  make build        Build Next.js production frontend"
	@echo "  make docker-up    Start Docker Compose containers"
	@echo "  make docker-down  Stop Docker Compose containers"

dev:
	@echo "Starting FastAPI server on http://127.0.0.1:8000..."
	python -m uvicorn apps.api.app.main:app --reload --port 8000

test:
	@echo "Running full test suite across all packages and services..."
	python -m pytest -v

test-fast:
	@echo "Running fast unit tests without network calls..."
	python -m pytest -k "not test_hermes_all_functions and not test_trading_firm" -v

backtest:
	@echo "Running Strategy DSL Backtest Engine..."
	python -m services.backtest_engine.engine

paper:
	@echo "Running Paper Trading Account Simulation..."
	python -c "from services.paper_trading.account import PaperTradingAccount; acc = PaperTradingAccount(); print(acc.get_portfolio_summary())"

agent:
	@echo "Running Hermes Supervisor Multi-Agent Trading Firm CLI..."
	python -m agents --symbol RELIANCE

acceptance:
	@echo "Executing Section 107 Autonomous Strategy Acceptance Test..."
	python scripts/acceptance_test.py

health:
	@echo "Running Section 109 Definition of Done Platform Health Audit..."
	python scripts/health_check.py

build:
	@echo "Building Next.js production bundle..."
	cd apps/web && npm run build

docker-up:
	@echo "Starting Docker Compose production cluster..."
	docker compose up -d

docker-down:
	@echo "Stopping Docker Compose containers..."
	docker compose down
