# Reconstructed review utility, not a byte-for-byte copy of the original local script.
# It flags unusual values for human review only; it never removes or changes source data.
$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $ProjectRoot
try {
    python .\scripts\check_extreme_values.py
    exit $LASTEXITCODE
} finally { Pop-Location }
