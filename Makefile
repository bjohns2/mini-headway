.PHONY: dev install seed test typecheck clean

dev: install
	@bash scripts/dev.sh

install:
	@echo "→ Installing backend deps..."
	@cd backend && uv sync --quiet
	@echo "→ Installing frontend deps..."
	@cd frontend && npm install --silent --no-audit --no-fund

seed:
	@cd backend && uv run python -m app.seed --reset

test:
	@cd backend && uv run pytest -q

typecheck:
	@cd backend && uv run mypy app
	@cd frontend && npm run typecheck

clean:
	@rm -f backend/mini-headway.db
	@rm -rf backend/.venv frontend/node_modules
