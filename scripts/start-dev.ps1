# start-dev.ps1 — Start backend + frontend dev servers (Windows PowerShell)
# Usage: .\scripts\start-dev.ps1
# Run from the repository root.
# Opens the backend in the current terminal and the frontend in a new window.
# Press Ctrl-C in each terminal to stop.

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "==> Starting backend on http://localhost:8000 ..."
# .venv is at the repository root; the new window activates it before running uvicorn.
$BackendCmd = if (Test-Path "$RepoRoot\.venv\Scripts\Activate.ps1") {
    "& '$RepoRoot\.venv\Scripts\Activate.ps1'; uvicorn main:app --reload --host 127.0.0.1 --port 8000"
} else {
    "uvicorn main:app --reload --host 127.0.0.1 --port 8000"
}

$BackendProcess = Start-Process powershell -ArgumentList (
    "-NoExit", "-Command",
    "Set-Location '$RepoRoot\backend'; $BackendCmd"
) -PassThru

Write-Host "==> Starting frontend on http://localhost:5173 ..."
$FrontendProcess = Start-Process powershell -ArgumentList (
    "-NoExit", "-Command",
    "Set-Location '$RepoRoot\frontend'; npm run dev"
) -PassThru

Write-Host ""
Write-Host "Both servers launched in separate windows."
Write-Host "Backend PID : $($BackendProcess.Id)"
Write-Host "Frontend PID: $($FrontendProcess.Id)"
Write-Host ""
Write-Host "Press ENTER here to stop both servers, or close their windows manually."
$null = Read-Host

Write-Host "==> Stopping servers..."
Stop-Process -Id $BackendProcess.Id  -Force -ErrorAction SilentlyContinue
Stop-Process -Id $FrontendProcess.Id -Force -ErrorAction SilentlyContinue
Write-Host "    Done."
