.PHONY: dev test lint

dev:
	docker compose up --build

test:
	cd backend && python -m pytest

lint:
	cd backend && python -m ruff check .
	cd frontend && pnpm lint

