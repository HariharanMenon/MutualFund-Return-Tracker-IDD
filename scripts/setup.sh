#!/usr/bin/env bash
# setup.sh — One-command dev environment setup (Mac / Linux)
# Usage: bash scripts/setup.sh
# Run from the repository root.

# Exit immediately if a command exits with a non-zero status
# Treat unset variables as an error, and catch pipeline failures
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Define explicit paths to virtual environment binaries to bypass activation scoping
VENV_PATH="$REPO_ROOT/.venv"
VENV_PYTHON="$VENV_PATH/bin/python3"
VENV_PIP="$VENV_PATH/bin/pip"

# Corporate/Firewall Bypass: Define trusted hosts for pip
TRUSTED_HOSTS=(
  "--trusted-host" "pypi.org"
  "--trusted-host" "files.pythonhosted.org"
  "--trusted-host" "pypi.python.org"
)

echo "==> Setting up backend Python virtual environment..."
# Create the venv if it doesn't already exist
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
fi

# Upgrade pip and install requirements using direct paths and trusted host flags
"$VENV_PYTHON" -m pip install --upgrade pip --quiet "${TRUSTED_HOSTS[@]}"
"$VENV_PIP" install -r "$REPO_ROOT/backend/requirements.txt" --quiet "${TRUSTED_HOSTS[@]}"
echo "    Backend .venv ready."

echo "==> Setting up frontend Node.js dependencies..."
# Use a subshell ( ... ) to change directories so we automatically 
# snap back to the previous directory when it finishes
(
    cd "$REPO_ROOT/frontend"
    # Note: If npm fails with a similar SSL error, uncomment the line below:
    # npm config set strict-ssl false
    npm install --silent
    echo "    Frontend node_modules ready."
)

echo ""
echo "Setup complete. To start both servers run:"
echo "  bash scripts/start-dev.sh"