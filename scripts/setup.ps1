# setup.ps1 — One-command dev environment setup (Windows PowerShell)
# Usage: .\scripts\setup.ps1
# Run from the repository root.

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "==> Setting up backend Python virtual environment..."
# .venv lives at the repository root; requirements.txt is in backend/
python -m venv "$RepoRoot\.venv"
& "$RepoRoot\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip --quiet
pip install -r "$RepoRoot\backend\requirements.txt" --quiet
deactivate
Write-Host "    Backend .venv ready."

Write-Host "==> Setting up frontend Node.js dependencies..."
Push-Location "$RepoRoot\frontend"
try {
    npm install --silent
    Write-Host "    Frontend node_modules ready."
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "Setup complete. To start both servers run:"
Write-Host "  .\scripts\start-dev.ps1"
