# Virtual VDS Launcher
# Runs the Python implementation of VDS (Virtual Dual Screen)

$ScriptDir = $PSScriptRoot
$MainPy = Join-Path $ScriptDir "main.py"

if (-not (Test-Path $MainPy)) {
    Write-Host "Error: main.py not found in $ScriptDir" -ForegroundColor Red
    exit 1
}

Write-Host "Starting VDS Virtual Environment..." -ForegroundColor Cyan
Write-Host "Running $MainPy" -ForegroundColor Gray

# Check if running in a venv, if not try to find one or just use 'python'
python $MainPy

if ($LASTEXITCODE -ne 0) {
    Write-Host "VDS exited with error code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "VDS Closed." -ForegroundColor Green
