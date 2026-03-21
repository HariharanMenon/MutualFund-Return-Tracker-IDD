# test-all.ps1 — Run backend pytest + frontend vitest (Windows PowerShell)
# Usage: .\scripts\test-all.ps1
# Run from the repository root.
# Exits with code 1 if any test suite fails.

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Failed   = $false

Write-Host "=============================="
Write-Host " Backend tests (pytest)"
Write-Host "=============================="
# venv is at the repository root; activate before pushing into backend/.
if (Test-Path "$RepoRoot\venv\Scripts\Activate.ps1") {
    & "$RepoRoot\venv\Scripts\Activate.ps1"
}
Push-Location "$RepoRoot\backend"
try {
    python -m pytest tests/ -v
    if ($LASTEXITCODE -ne 0) { $Failed = $true }
    if (Get-Command deactivate -ErrorAction SilentlyContinue) { deactivate }
}
catch {
    Write-Warning "Backend tests raised an exception: $_"
    $Failed = $true
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "=============================="
Write-Host " Frontend tests (vitest)"
Write-Host "=============================="
Push-Location "$RepoRoot\frontend"
try {
    npm run test
    if ($LASTEXITCODE -ne 0) { $Failed = $true }
}
catch {
    Write-Warning "Frontend tests raised an exception: $_"
    $Failed = $true
}
finally {
    Pop-Location
}

Write-Host ""
if (-not $Failed) {
    Write-Host "All tests passed."
} else {
    Write-Error "One or more test suites FAILED."
    exit 1
}
