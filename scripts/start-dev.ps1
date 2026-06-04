# start-dev.ps1 — Start backend + frontend dev servers (Windows PowerShell)
# Usage: .\scripts\start-dev.ps1
# Run from the repository root.
# Opens the backend in the current terminal and the frontend in a new window.
# Press Ctrl-C in each terminal to stop.

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoRoot = Split-Path -Parent $PSScriptRoot

# Define explicit paths to execution tools
$VenvUvicorn = Join-Path $RepoRoot ".venv\Scripts\uvicorn.exe"
$BackendDir  = Join-Path $RepoRoot "backend"
$FrontendDir = Join-Path $RepoRoot "frontend"

# Fallback to global uvicorn if venv doesn't exist
$UvicornCmd = if (Test-Path $VenvUvicorn) { $VenvUvicorn } else { "uvicorn" }

Write-Host "==> Starting backend on http://localhost:8000 ..."
# Use a cleaner, single-string format for -ArgumentList to avoid nested quoting bugs
$BackendProcess = Start-Process powershell -ArgumentList "-NoExit -Command `"Set-Location '$BackendDir'; & '$UvicornCmd' main:app --reload --host 127.0.0.1 --port 8000`"" -PassThru

Write-Host "==> Starting frontend on http://localhost:5173 ..."
$FrontendProcess = Start-Process powershell -ArgumentList "-NoExit -Command `"Set-Location '$FrontendDir'; npm run dev`"" -PassThru

Write-Host ""
Write-Host "Both servers launched in separate windows."
Write-Host "Backend Terminal PID : $($BackendProcess.Id)"
Write-Host "Frontend Terminal PID: $($FrontendProcess.Id)"
Write-Host ""
Write-Host "Press ENTER here to stop both servers, or close their windows manually."
$null = Read-Host

Write-Host "==> Stopping servers and cleaning up ports..."

# Helper function to kill the window AND any child processes (Node / Python / Uvicorn) it spawned
function Stop-ProcessTree ($ParentPid) {
    if ($ParentPid) {
        # Visual/Graceful window close first
        Stop-Process -Id $ParentPid -Force -ErrorAction SilentlyContinue
        
        # WMI lookup to catch orphaned child processes holding the ports
        Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $ParentPid } | ForEach-Object {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
    }
}

Stop-ProcessTree -ParentPid $BackendProcess.Id
Stop-ProcessTree -ParentPid $FrontendProcess.Id

Write-Host "    Done. Ports 8000 and 5173 freed."