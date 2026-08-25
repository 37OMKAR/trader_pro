# Market AI Monorepo Makefile

.PHONY: test test-py test-web dev dev-api dev-web install migrate

install:
	pip install -r apps/api/requirements.txt
	cd apps/web && npm install

dev-api:
	python -m uvicorn apps.api.app.main:app --reload --port 8000 --host 127.0.0.1

dev-web:
	cd apps/web && npm run dev

dev:
	@echo "Starting FastAPI Backend and Next.js Web Terminal..."

test-py:
	python -m pytest

test-web:
	cd apps/web && npm run lint

test: test-py test-web
