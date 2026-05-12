#!/usr/bin/env bash
#
# Runs once, when the codespace is first created. Installs the things the
# image doesn't ship with (uv, Claude Code CLI), then installs project deps
# and seeds the SQLite database so the candidate's first `make dev` is fast.

set -euo pipefail

cd "$(dirname "$0")/.."
ROOT="$PWD"

echo "→ Installing uv (Python package manager)..."
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
# Persist for future shells.
if ! grep -q '.local/bin' ~/.bashrc 2>/dev/null; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

echo "→ Installing Claude Code CLI globally..."
npm install -g @anthropic-ai/claude-code || \
  echo "  (Claude Code install failed — candidate can install it themselves with 'npm install -g @anthropic-ai/claude-code'.)"

echo "→ Installing backend dependencies..."
cd "$ROOT/backend"
uv sync

echo "→ Seeding database..."
rm -f mini-headway.db
uv run python -m app.seed --reset

echo "→ Installing frontend dependencies..."
cd "$ROOT/frontend"
npm install --no-audit --no-fund

echo ""
echo "✓ Codespace ready."
echo ""
echo "  Run 'make dev' to start both servers. The Vite preview will pop up"
echo "  automatically at port 5173, backend on 8000."
echo ""
echo "  AI tools pre-installed:"
echo "    • GitHub Copilot — sign in via the VS Code account icon"
echo "    • Claude Code    — run 'claude' in the terminal (sign in on first run)"
