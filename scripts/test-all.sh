#!/usr/bin/env bash
# test-all.sh — Run backend pytest + frontend vitest (Mac / Linux)
# Usage: bash scripts/test-all.sh
# Run from the repository root.
# Exits non-zero if any test suite fails.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0

echo "=============================="
echo " Backend tests (pytest)"
echo "=============================="
# venv is at the repository root; activate before cd-ing into backend/.
if [ -f "$REPO_ROOT/venv/bin/activate" ]; then
    # shellcheck disable=SC1091
    source "$REPO_ROOT/venv/bin/activate"
fi
cd "$REPO_ROOT/backend"
python -m pytest tests/ -v || FAILED=1

echo ""
echo "=============================="
echo " Frontend tests (vitest)"
echo "=============================="
cd "$REPO_ROOT/frontend"
npm run test || FAILED=1

echo ""
if [ "$FAILED" -eq 0 ]; then
    echo "All tests passed."
else
    echo "One or more test suites FAILED." >&2
    exit 1
fi
