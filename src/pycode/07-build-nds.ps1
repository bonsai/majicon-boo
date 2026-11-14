param(
    [string]$DevkitRoot = "C:\devkitPro",
    [string]$ProjectRoot
)

# If ProjectRoot is not provided, assume parent directory of this script (VDS root)
if (-not $ProjectRoot) {
    $ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
}

if (-not (Test-Path $ProjectRoot)) {
    Write-Host ("Project root not found: " + $ProjectRoot) -ForegroundColor Red
    exit 1
}

$root = $Env:DEVKITPRO
if (-not $root) {
    $root = $DevkitRoot
}

if (-not (Test-Path $root)) {
    Write-Host ("devkitPro root not found: " + $root) -ForegroundColor Red
    exit 1
}

$devkitArmPath = Join-Path $root "devkitARM"

$devkitProForMsys = $root.Replace("\", "/")
$devkitArmForMsys = $devkitArmPath.Replace("\", "/")

$Env:DEVKITPRO = $devkitProForMsys
$Env:DEVKITARM = $devkitArmForMsys
[Environment]::SetEnvironmentVariable("DEVKITPRO", $root, "User")
[Environment]::SetEnvironmentVariable("DEVKITARM", $devkitArmPath, "User")

Write-Host ("DEVKITPRO=" + $Env:DEVKITPRO) -ForegroundColor Green
Write-Host ("DEVKITARM=" + $Env:DEVKITARM) -ForegroundColor Green

$devkitArmBin = Join-Path $devkitArmPath "bin"
if (Test-Path $devkitArmBin) {
    if ($Env:Path -notlike "*" + $devkitArmBin + "*") {
        $Env:Path = $devkitArmBin + ";" + $Env:Path
    }
}

function Get-MakeDir {
    param([string]$Root)
    $candidates = @(
        (Join-Path $Root "msys2\usr\bin"),
        (Join-Path $Root "msys\usr\bin")
    )
    foreach ($c in $candidates) {
        $m = Join-Path $c "make.exe"
        if (Test-Path $m) {
            return $c
        }
    }
    return $null
}

$makeDir = Get-MakeDir -Root $root

if (-not $makeDir) {
    Write-Host "make.exe not found under devkitPro. Check your installation." -ForegroundColor Red
    exit 1
}

Write-Host ("Using make from " + $makeDir) -ForegroundColor Green

if ($Env:Path -notlike "*" + $makeDir + "*") {
    $Env:Path = $makeDir + ";" + $Env:Path
}

Push-Location $ProjectRoot

Write-Host "Running make to build hw.nds..." -ForegroundColor Cyan
make

if ($LASTEXITCODE -ne 0) {
    Write-Host ("make failed with exit code " + $LASTEXITCODE) -ForegroundColor Red
    Pop-Location
    exit $LASTEXITCODE
}

$nds = Get-ChildItem -Path $ProjectRoot -Filter "hw.nds" -Recurse -ErrorAction SilentlyContinue |
    Select-Object -First 1

if ($nds) {
    Write-Host ("Build succeeded. Found hw.nds at " + $nds.FullName) -ForegroundColor Green
    
    # Copy to pycode with timestamp
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $dest = Join-Path $PSScriptRoot ("veep_" + $timestamp + ".nds")
    Copy-Item $nds.FullName -Destination $dest -Force
    Write-Host ("Copied to " + $dest) -ForegroundColor Green
} else {
    Write-Host "Build succeeded, but hw.nds was not found." -ForegroundColor Yellow
}

Pop-Location
