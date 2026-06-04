#!/usr/bin/env bash
# start-dev.sh — Start backend + frontend dev servers concurrently (Mac / Linux)
# Usage: bash scripts/start-dev.sh
# Run from the repository root.
# Press Ctrl-C to stop both servers.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Define explicit paths to execution tools to bypass virtualenv 'source' leakage
VENV_UVICORN="$REPO_ROOT/.venv/bin/uvicorn"
BACKEND_DIR="$REPO_ROOT/backend"
FRONTEND_DIR="$REPO_ROOT/frontend"

# Fallback to global uvicorn if venv doesn't exist
if [ -f "$VENV_UVICORN" ]; then
    UVICORN_CMD="$VENV_UVICORN"
else
    UVICORN_CMD="uvicorn"
fi

cleanup() {
    echo ""
    echo "==> Stopping servers and cleaning up ports..."
    
    # Kill the entire process group rather than just the single parent PID.
    # This ensures child sub-processes (Node workers, Uvicorn reloaders) are terminated.
    if [ -n "${BACKEND_PID:-}" ]; then
        pkill -P "$BACKEND_PID" 2>/dev/null || true
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    
    if [ -n "${FRONTEND_PID:-}" ]; then
        pkill -P "$FRONTEND_PID" 2>/dev/null || true
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi
    
    echo "    Done. Ports 8000 and 5173 freed."
}
# Trap exit signals to ensure cleanup runs
trap cleanup EXIT INT TERM

echo "==> Starting backend on http://localhost:8000 ..."
# Run backend inside a cleanly scoped subshell context
(
    cd "$BACKEND_DIR"
    exec "$UVICORN_CMD" main:app --reload --host 127.0.0.1 --port 8000
) &
BACKEND_PID=$!

echo "==> Starting frontend on http://localhost:5173 ..."
# Run frontend inside a cleanly scoped subshell context
(
    cd "$FRONTEND_DIR"
    exec npm run dev
) &
FRONTEND_PID=$!

echo ""
echo "Both servers running concurrently. Press Ctrl-C to stop."

# Wait cleanly for the background processes
wait