#!/usr/bin/env bash
#
# Runs every time the codespace starts (including the first time, after
# post-create). Auto-launches both dev servers so the preview panel works
# without the candidate having to type anything.

set -euo pipefail

cd "$(dirname "$0")/.."
ROOT="$PWD"
export PATH="$HOME/.local/bin:$PATH"

# Skip if already running (e.g. on rebuild without container recreate).
if curl -fs http://localhost:5173 >/dev/null 2>&1 \
  && curl -fs http://localhost:8000/api/health >/dev/null 2>&1; then
  echo "✓ Servers already running."
  exit 0
fi

echo "→ Starting backend on :8000..."
cd "$ROOT/backend"
nohup uv run uvicorn app.main:app --port 8000 --host 0.0.0.0 \
  > /tmp/backend.log 2>&1 &

echo "→ Starting frontend on :5173..."
cd "$ROOT/frontend"
nohup npm run dev -- --host 0.0.0.0 \
  > /tmp/frontend.log 2>&1 &

cd "$ROOT"
echo ""
echo "  Logs: /tmp/backend.log, /tmp/frontend.log"
echo "  Stop: pkill -f uvicorn; pkill -f vite"
