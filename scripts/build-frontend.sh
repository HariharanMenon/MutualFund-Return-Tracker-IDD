#!/usr/bin/env bash
# build-frontend.sh — Build the React + Vite frontend for production (Mac / Linux)
# Usage: bash scripts/build-frontend.sh
# Run from the repository root.
# Output: frontend/dist/  (Render deploys this directory as a static site)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Building frontend..."
cd "$REPO_ROOT/frontend"
npm install --silent
npm run build
echo "    Build complete. Output: frontend/dist/"
