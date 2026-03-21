# build-frontend.ps1 — Build the React + Vite frontend for production (Windows PowerShell)
# Usage: .\scripts\build-frontend.ps1
# Run from the repository root.
# Output: frontend\dist\  (Render deploys this directory as a static site)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "==> Building frontend..."
Push-Location "$RepoRoot\frontend"
try {
    npm install --silent
    npm run build
    Write-Host "    Build complete. Output: frontend\dist\"
}
finally {
    Pop-Location
}
