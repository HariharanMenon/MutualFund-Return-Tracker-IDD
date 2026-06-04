# setup.ps1 — One-command dev environment setup (Windows PowerShell)
# Usage: .\scripts\setup.ps1
# Run from the repository root.

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

# $PSScriptRoot is root/scripts, so Parent is the repository root
$RepoRoot = Split-Path -Parent $PSScriptRoot

# Define explicit paths to avoid scope/activation issues
$VenvPath = Join-Path $RepoRoot ".venv"
$VenvPip  = Join-Path $VenvPath "Scripts\pip.exe"
$VenvPy   = Join-Path $VenvPath "Scripts\python.exe"

# Corporate/Firewall Bypass: Define trusted hosts for pip
$TrustedHosts = @("--trusted-host", "pypi.org", "--trusted-host", "files.pythonhosted.org", "--trusted-host", "pypi.python.org")

Write-Host "==> Setting up backend Python virtual environment..."
# Create the venv if it doesn't exist
if (-not (Test-Path $VenvPath)) {
    python -m venv $VenvPath
}

# Upgrade pip and install requirements using trusted host flags to bypass corporate SSL decryption issues
& $VenvPy -m pip install --upgrade pip --quiet $TrustedHosts
& $VenvPip install -r "$RepoRoot\backend\requirements.txt" --quiet $TrustedHosts
Write-Host "    Backend .venv ready."

Write-Host "==> Setting up frontend Node.js dependencies..."
Push-Location "$RepoRoot\frontend"
try {
    # Note: If npm fails with a similar SSL error, you may need to run: npm config set strict-ssl false
    & npm install --silent
    
    # Check if the external process failed
    if ($LASTEXITCODE -ne 0) {
        throw "npm install failed with exit code $LASTEXITCODE"
    }
    Write-Host "    Frontend node_modules ready."
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "Setup complete. To start both servers run:"
Write-Host "  .\scripts\start-dev.ps1"