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

# Recursively kill a process and all its descendants (bottom-up)
kill_tree() {
    local pid=$1
    # Find and recursively kill children first
    local children
    children=$(pgrep -P "$pid" 2>/dev/null || true)
    for child in $children; do
        kill_tree "$child"
    done
    # Then kill the parent
    kill "$pid" 2>/dev/null || true
}

# Safety net: kill any process still holding a given port
kill_port() {
    local port=$1
    local pids
    if command -v lsof &>/dev/null; then
        pids=$(lsof -ti tcp:"$port" 2>/dev/null || true)
    else
        # fallback for systems without lsof (e.g. minimal Linux containers)
        pids=$(ss -tlnp "sport = :$port" 2>/dev/null |
               grep -oP 'pid=\K[0-9]+' || true)
    fi
    for p in $pids; do
        kill -9 "$p" 2>/dev/null || true
    done
}

cleanup() {
    echo ""
    echo "==> Stopping servers and cleaning up ports..."

    [ -n "${BACKEND_PID:-}"  ] && kill_tree "$BACKEND_PID"
    [ -n "${FRONTEND_PID:-}" ] && kill_tree "$FRONTEND_PID"

    # Safety net: kill anything still holding port 8000 or 5173
    kill_port 8000
    kill_port 5173

    echo "    Done. Ports 8000 and 5173 freed."
}

# Trap exit signals to ensure cleanup runs
trap cleanup EXIT INT TERM

echo "==> Starting backend on http://localhost:8000 ..."
(
    cd "$BACKEND_DIR"
    exec "$UVICORN_CMD" main:app --reload --host 127.0.0.1 --port 8000
) &
BACKEND_PID=$!

echo "==> Starting frontend on http://localhost:5173 ..."
(
    cd "$FRONTEND_DIR"
    exec npm run dev
) &
FRONTEND_PID=$!

echo ""
echo "Both servers running concurrently. Press Ctrl-C to stop."

# Wait cleanly for the background processes
wait