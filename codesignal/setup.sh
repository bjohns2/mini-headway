#!/usr/bin/env bash
#
# Bootstrap script for a CodeSignal Interview session.
#
# Two-mode boot:
#   • If the repo's source is already present in or near $PWD (i.e. it was
#     pre-uploaded into the CodeSignal starting filesystem), use it in place.
#   • Otherwise clone the source from GitHub. This is the default path —
#     it keeps the starting filesystem nearly empty so CodeSignal's 1 MB
#     filesystem cap isn't a problem.
#
# After locating/cloning the source, this script:
#   1. Installs uv (Python package manager) if missing.
#   2. Installs the backend's Python deps + Python 3.11 via uv.
#   3. Installs the frontend's Node deps via npm.
#   4. Seeds the SQLite database with the interview fixture.
#   5. Starts the backend (uvicorn on :8000) and the frontend (vite on :3000)
#      in the background so the candidate's preview panel works on session
#      start.
#
# The candidate sees a ready terminal at the repo root. They can poke around
# with `ls`, read README.md, and start clicking in the preview panel.

set -euo pipefail

REPO_URL="${MINI_HEADWAY_REPO_URL:-https://github.com/bjohns2/mini-headway.git}"

has_repo() {
  [ -d "$1/backend" ] && [ -d "$1/frontend" ]
}

find_existing_repo() {
  # 1. Current directory.
  if has_repo "$PWD"; then echo "$PWD"; return 0; fi

  # 2. Search downward from PWD (depth-limited so it stays quick).
  local found
  found="$(find "$PWD" -maxdepth 4 -type d -name backend 2>/dev/null \
    | while IFS= read -r d; do
        local parent
        parent="$(dirname "$d")"
        if has_repo "$parent"; then echo "$parent"; break; fi
      done | head -n 1)"
  if [ -n "$found" ]; then echo "$found"; return 0; fi

  # 3. Walk upward from PWD.
  local cur="$PWD"
  while [ "$cur" != "/" ]; do
    if has_repo "$cur"; then echo "$cur"; return 0; fi
    cur="$(dirname "$cur")"
  done

  return 1
}

if ROOT="$(find_existing_repo)"; then
  echo "→ Found existing source at $ROOT"
else
  CLONE_DIR="${PWD}/mini-headway"
  echo "→ No source on disk. Cloning $REPO_URL into $CLONE_DIR..."
  git clone --depth 1 "$REPO_URL" "$CLONE_DIR"
  ROOT="$CLONE_DIR"
fi
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
echo "  Repo:     $ROOT"
echo "  Backend:  http://localhost:8000 (logs: /tmp/backend.log)"
echo "  Frontend: http://localhost:3000 (logs: /tmp/frontend.log)"
echo ""
echo "  Read README.md for the interview task."
