#!/usr/bin/env bash
# clean.sh — Remove generated artefacts (Mac / Linux)
# Usage: bash scripts/clean.sh
# Run from the repository root.
# Removes: .venv/ (root), frontend/node_modules, frontend/dist,
#           __pycache__ trees, .pytest_cache, vitest cache.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "==> Removing Python virtual environment (root/.venv)..."
rm -rf .venv

echo "==> Removing Python cache files..."
find . -type d -name "__pycache__" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -not -path "./.git/*" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -not -path "./.git/*" -delete 2>/dev/null || true

echo "==> Removing frontend node_modules..."
rm -rf frontend/node_modules

echo "==> Removing frontend build output..."
rm -rf frontend/dist

echo "==> Removing frontend test cache..."
rm -rf frontend/.vitest 2>/dev/null || true

echo "Clean complete."
