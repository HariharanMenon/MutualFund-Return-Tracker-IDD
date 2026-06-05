# test-all.ps1 — Run backend pytest + frontend vitest (Windows PowerShell)
# Usage: .\scripts\test-all.ps1
# Run from the repository root.
# Exits with code 1 if any test suite fails.

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# If scripts/test-all.ps1, $PSScriptRoot is repo/scripts. Parent is repo root.
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Failed   = $false

# Define paths to executables
$PytestExe = "$RepoRoot\.venv\Scripts\pytest.exe"
$NpmExe    = Get-Command npm -ErrorAction SilentlyContinue

# --------------------------------------------
# Backend Tests (pytest)
# --------------------------------------------
Write-Host "=============================="
Write-Host " Backend tests (pytest)"
Write-Host "=============================="

if (-not (Test-Path $PytestExe)) {
    Write-Warning "Virtual environment or pytest not found at: $PytestExe"
    $Failed = $true
} else {
    Push-Location "$RepoRoot\backend"
    try {
        # Directly call the venv's pytest executable (no activation required)
        & $PytestExe tests/ -v
        if ($LASTEXITCODE -ne 0) { $Failed = $true }
    }
    catch {
        Write-Warning "Backend tests failed to execute: $_"
        $Failed = $true
    }
    finally {
        Pop-Location
    }
}

# --------------------------------------------
# Frontend Tests (vitest)
# --------------------------------------------
Write-Host "`n=============================="
Write-Host " Frontend tests (vitest)"
Write-Host "=============================="

if (-not $NpmExe) {
    Write-Warning "Node.js/npm is not installed or not in PATH."
    $Failed = $true
} else {
    Push-Location "$RepoRoot\frontend"
    try {
        # Using cmd /c ensures npm executes predictably on Windows PowerShell
        cmd /c npm run test
        if ($LASTEXITCODE -ne 0) { $Failed = $true }
    }
    catch {
        Write-Warning "Frontend tests failed to execute: $_"
        $Failed = $true
    }
    finally {
        Pop-Location
    }
}

# --------------------------------------------
# Test Results Execution
# --------------------------------------------
Write-Host ""
if (-not $Failed) {
    Write-Host "All tests passed successfully!" -ForegroundColor Green
    exit 0
} else {
    # Using Write-Host for the error avoids a messy PowerShell script stack trace
    Write-Host "One or more test suites FAILED." -ForegroundColor Red
    exit 1
}