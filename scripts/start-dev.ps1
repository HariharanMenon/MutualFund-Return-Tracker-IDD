# start-dev.ps1 — Start backend + frontend dev servers (Windows PowerShell)
# Usage: .\scripts\start-dev.ps1
# Run from the repository root.
# Opens the backend in the current terminal and the frontend in a new window.
# Press ENTER in this terminal to stop both servers.

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

# Recursively kill a process and all its descendants (bottom-up)
function Stop-ProcessTree ($ParentPid) {
    if (-not $ParentPid) { return }
    # Kill all children recursively first (bottom-up)
    Get-CimInstance Win32_Process |
        Where-Object { $_.ParentProcessId -eq $ParentPid } |
        ForEach-Object { Stop-ProcessTree -ParentPid $_.ProcessId }
    # Then kill the parent itself
    Stop-Process -Id $ParentPid -Force -ErrorAction SilentlyContinue
}

Stop-ProcessTree -ParentPid $BackendProcess.Id
Stop-ProcessTree -ParentPid $FrontendProcess.Id

# Safety net: kill anything still LISTENING/ESTABLISHED on port 8000 or 5173
# Handles edge cases where PID tracking failed (e.g. server window was manually restarted)
foreach ($port in @(8000, 5173)) {
    $pids = netstat -ano |
        Select-String ":$port\s" |
        ForEach-Object { ($_ -split '\s+')[-1] } |
        Where-Object { $_ -match '^\d+$' -and $_ -ne '0' } |
        Sort-Object -Unique
    foreach ($p in $pids) {
        Stop-Process -Id ([int]$p) -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "    Done. Ports 8000 and 5173 freed."