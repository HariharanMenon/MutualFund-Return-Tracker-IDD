#!/usr/bin/env bash
# test-all.sh — Run backend pytest + frontend vitest (Mac / Linux)
# Usage: ./scripts/test-all.sh
# Run from the repository root.
# Exits non-zero if any test suite fails.

set -euo pipefail

# Get the directory of the script, then go up one level to the repo root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0

# Define paths to executables
PYTEST_EXE="$REPO_ROOT/.venv/bin/pytest"

# Color codes for clean UI output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --------------------------------------------
# Backend Tests (pytest)
# --------------------------------------------
echo "=============================="
echo " Backend tests (pytest)"
echo "=============================="

if [ ! -x "$PYTEST_EXE" ]; then
    echo "Warning: Virtual environment or pytest executable not found at: $PYTEST_EXE" >&2
    FAILED=1
elif [ ! -d "$REPO_ROOT/backend" ]; then
    echo "Warning: Backend directory missing at $REPO_ROOT/backend" >&2
    FAILED=1
else
    # Wrap in a subshell ( ... ) so directory changes don't affect the rest of the script
    (
        cd "$REPO_ROOT/backend"
        # Run pytest directly from the .venv without activating
        "$PYTEST_EXE" tests/ -v
    ) || FAILED=1
fi

# --------------------------------------------
# Frontend Tests (vitest)
# --------------------------------------------
echo ""
echo "=============================="
echo " Frontend tests (vitest)"
echo "=============================="

if ! command -v npm &> /dev/null; then
    echo "Warning: Node.js/npm is not installed or not in PATH." >&2
    FAILED=1
elif [ ! -d "$REPO_ROOT/frontend" ]; then
    echo "Warning: Frontend directory missing at $REPO_ROOT/frontend" >&2
    FAILED=1
else
    (
        cd "$REPO_ROOT/frontend"
        npm run test
    ) || FAILED=1
fi

# --------------------------------------------
# Test Results Execution
# --------------------------------------------
echo ""
if [ "$FAILED" -eq 0 ]; then
    echo -e "${GREEN}All tests passed successfully!${NC}"
    exit 0
else
    echo -e "${RED}One or more test suites FAILED.${NC}" >&2
    exit 1
fi