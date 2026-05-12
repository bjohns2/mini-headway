#!/usr/bin/env bash
#
# Bootstrap script for a CodeSignal Interview session.
#
# Assumes the repo files have already been pre-loaded into the CodeSignal
# container (i.e. you uploaded the project when creating the Advanced
# Assessment Question — no `git clone` needed).
#
# What this does:
#   1. Installs uv (Python package manager) if missing.
#   2. Installs the backend's Python deps + Python 3.11 via uv.
#   3. Installs the frontend's Node deps via npm.
#   4. Seeds the SQLite database with the interview fixture.
#   5. Starts the backend (uvicorn on :8000) and frontend (vite on :3000)
#      in the background so the candidate's preview panel works on session start.
#
# The candidate sees a ready terminal at the repo root. They can poke around
# with `ls`, read README.md, and start clicking in the preview panel.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "→ Installing uv (Python package manager)..."
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "→ Installing backend dependencies..."
cd "$ROOT/backend"
uv sync --quiet

echo "→ Seeding database..."
rm -f mini-headway.db
uv run python -m app.seed --reset

echo "→ Installing frontend dependencies..."
cd "$ROOT/frontend"
npm install --silent --no-audit --no-fund

echo "→ Starting servers in the background..."
cd "$ROOT/backend"
nohup uv run uvicorn app.main:app --port 8000 --host 0.0.0.0 \
  > /tmp/backend.log 2>&1 &

cd "$ROOT/frontend"
# CodeSignal's preview panel only shows port 3000, so override Vite's default
# of 5173 here. The repo's own scripts still use 5173 for local dev.
nohup npm run dev -- --port 3000 --host 0.0.0.0 \
  > /tmp/frontend.log 2>&1 &

cd "$ROOT"
echo ""
echo "✓ Setup complete."
echo ""
echo "  Backend:  http://localhost:8000 (logs: /tmp/backend.log)"
echo "  Frontend: http://localhost:3000 (logs: /tmp/frontend.log)"
echo ""
echo "  Read README.md for the interview task."
