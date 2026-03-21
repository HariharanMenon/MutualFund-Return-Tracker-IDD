#!/usr/bin/env bash
# start-dev.sh — Start backend + frontend dev servers concurrently (Mac / Linux)
# Usage: bash scripts/start-dev.sh
# Run from the repository root.
# Press Ctrl-C to stop both servers.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cleanup() {
    echo ""
    echo "==> Stopping servers..."
    kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
    wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
    echo "    Done."
}
trap cleanup EXIT INT TERM

echo "==> Starting backend on http://localhost:8000 ..."
# venv is at the repository root; activate before cd-ing into backend/.
if [ -f "$REPO_ROOT/venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$REPO_ROOT/venv/bin/activate"
fi
cd "$REPO_ROOT/backend"
uvicorn main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo "==> Starting frontend on http://localhost:5173 ..."
cd "$REPO_ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Both servers running. Press Ctrl-C to stop."
wait
