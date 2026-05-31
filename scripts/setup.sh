#!/usr/bin/env bash
# setup.sh — One-command dev environment setup (Mac / Linux)
# Usage: bash scripts/setup.sh
# Run from the repository root.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "==> Setting up backend Python virtual environment..."
# .venv lives at the repository root; requirements.txt is in backend/
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -r backend/requirements.txt --quiet
deactivate
echo "    Backend .venv ready."

echo "==> Setting up frontend Node.js dependencies..."
cd "$REPO_ROOT/frontend"
npm install --silent
echo "    Frontend node_modules ready."

echo ""
echo "Setup complete. To start both servers run:"
echo "  bash scripts/start-dev.sh"
