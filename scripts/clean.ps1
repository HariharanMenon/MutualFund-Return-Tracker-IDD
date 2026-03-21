# clean.ps1 — Remove generated artefacts (Windows PowerShell)
# Usage: .\scripts\clean.ps1
# Run from the repository root.
# Removes: .venv\ (root), frontend\node_modules, frontend\dist,
#           __pycache__ trees, .pytest_cache, vitest cache.

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoRoot = Split-Path -Parent $PSScriptRoot

function Remove-IfExists {
    param([string]$Path)
    if (Test-Path $Path) {
        Remove-Item $Path -Recurse -Force
        Write-Host "    Removed: $Path"
    }
}

Write-Host "==> Removing Python virtual environment (root\.venv)..."
Remove-IfExists "$RepoRoot\.venv"

Write-Host "==> Removing Python cache files..."
Get-ChildItem -Path $RepoRoot -Filter "__pycache__" -Recurse -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\.git\\' } |
    ForEach-Object { Remove-Item $_.FullName -Recurse -Force }

Get-ChildItem -Path $RepoRoot -Filter ".pytest_cache" -Recurse -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\.git\\' } |
    ForEach-Object { Remove-Item $_.FullName -Recurse -Force }

Get-ChildItem -Path $RepoRoot -Filter "*.pyc" -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\.git\\' } |
    ForEach-Object { Remove-Item $_.FullName -Force }

Write-Host "==> Removing frontend node_modules..."
Remove-IfExists "$RepoRoot\frontend\node_modules"

Write-Host "==> Removing frontend build output..."
Remove-IfExists "$RepoRoot\frontend\dist"

Write-Host "==> Removing frontend test cache..."
Remove-IfExists "$RepoRoot\frontend\.vitest"

Write-Host "Clean complete."
