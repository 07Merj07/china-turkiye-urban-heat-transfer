# Reconstructed compatibility wrapper for the GitHub repository.
# It checks the current source files and then runs the post-run validator.
$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $ProjectRoot
try {
    python .\scripts\build_city_mapping.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    python .\scripts\audit_uhi_sources.py
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    python .\scripts\phase2_validate_outputs.py --project-dir .
    exit $LASTEXITCODE
} finally { Pop-Location }
