#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cleanup() {
  echo ""
  echo "→ Shutting down dev servers..."
  kill 0 2>/dev/null || true
}
trap cleanup INT TERM EXIT

echo "→ Starting backend on http://localhost:8000"
(cd "$ROOT/backend" && uv run uvicorn app.main:app --reload --port 8000) &

echo "→ Starting frontend on http://localhost:5173"
(cd "$ROOT/frontend" && npm run dev -- --host) &

wait
