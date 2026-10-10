# UHII Extreme-Value Review
# Place this script in the project's scripts folder.
# It scans selected monthly files and flags values outside -40 to +40 for review.
# Flags are not automatic errors; this script does not change source data.
# Reports are written to data\audit_reports.

$ErrorActionPreference = 'Stop'

# Resolve the project root from this script's location: project\scripts\this-file.ps1
$projectRoot = Split-Path -Parent $PSScriptRoot
$dataDir = Join-Path $projectRoot 'data'
$folder = Join-Path $dataDir 'UHII_dataset'
$mappingPath = Join-Path $dataDir 'CityInfo_with_Country.csv'
$reportDir = Join-Path $dataDir 'audit_reports'
$reportPath = Join-Path $reportDir 'UHII_Extreme_Values_Check.csv'
$errorReportPath = Join-Path $reportDir 'UHII_Extreme_Values_Read_Errors.csv'

$columns = @('Intensity_EA', 'Intensity_IEA', 'Intensity_MEA', 'Intensity_DEA')
$culture = [System.Globalization.CultureInfo]::InvariantCulture
$countryById = @{}

if (-not (Test-Path -LiteralPath $folder -PathType Container)) {
    throw "UHII data folder not found: $folder. Check that data\UHII_dataset exists."
}
if (-not (Test-Path -LiteralPath $mappingPath -PathType Leaf)) {
    throw "Country mapping file not found: $mappingPath. Check that data\CityInfo_with_Country.csv exists."
}
if (-not (Test-Path -LiteralPath $reportDir -PathType Container)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

Write-Host '[1/3] Loading country mapping...' -ForegroundColor Cyan
Import-Csv -LiteralPath $mappingPath -Encoding UTF8 | ForEach-Object {
    $countryById[[string]$_.UrbanId] = [string]$_.Country
}

$files = @(
    Get-ChildItem -LiteralPath $folder -Filter '*.csv' -File |
        Where-Object { $_.BaseName -match '^(Mod1|Myd1|Myd2)_(Day|Nig)_\d{4}_(?:[1-9]|1[0-2])$' } |
        Sort-Object Name
)

if ($files.Count -eq 0) {
    throw "No matching Mod1/Myd1/Myd2 CSV files found in $folder."
}

$extremes = [System.Collections.Generic.List[object]]::new()
$readErrorsList = [System.Collections.Generic.List[object]]::new()
$total = $files.Count
$index = 0

Write-Host "[2/3] Scanning $total files for values below -40 or above 40. These are flags for review, not automatic errors." -ForegroundColor Cyan

foreach ($file in $files) {
    $index++
    try {
        Import-Csv -LiteralPath $file.FullName -Encoding UTF8 -ErrorAction Stop | ForEach-Object {
            $row = $_
            $id = [string]$row.UrbanId
            $country = if ($countryById.ContainsKey($id)) { $countryById[$id] } else { 'UNKNOWN_ID' }

            foreach ($column in $columns) {
                $raw = [string]$row.$column
                if (-not [string]::IsNullOrWhiteSpace($raw) -and $raw -ne 'NA') {
                    $value = 0.0
                    $parsed = [double]::TryParse(
                        $raw,
                        [System.Globalization.NumberStyles]::Float,
                        $culture,
                        [ref]$value
                    )
                    if ($parsed -and ($value -lt -40 -or $value -gt 40)) {
                        $extremes.Add([PSCustomObject]@{
                            File = $file.Name
                            Country = $country
                            UrbanId = $id
                            Method = $column
                            Value = $value
                        })
                    }
                }
            }
        }
    }
    catch {
        $readErrorsList.Add([PSCustomObject]@{
            File = $file.Name
            Error = $_.Exception.Message
        })
    }

    $percent = [math]::Round(($index / $total) * 100, 1)
    Write-Progress -Activity 'UHII extreme-value review' -Status "$index / $total files ($percent%)" -PercentComplete (($index / $total) * 100)
    if (($index % 25 -eq 0) -or ($index -eq $total)) {
        Write-Host "Scanned $index / $total files ($percent%). Flagged cells: $($extremes.Count); read errors: $($readErrorsList.Count)"
    }
}

Write-Progress -Activity 'UHII extreme-value review' -Completed
Write-Host '[3/3] Saving reports...' -ForegroundColor Cyan

if ($extremes.Count -gt 0) {
    $extremes | Export-Csv -LiteralPath $reportPath -NoTypeInformation -Encoding UTF8
} else {
    'File,Country,UrbanId,Method,Value' | Set-Content -LiteralPath $reportPath -Encoding UTF8
}

if ($readErrorsList.Count -gt 0) {
    $readErrorsList | Export-Csv -LiteralPath $errorReportPath -NoTypeInformation -Encoding UTF8
} elseif (Test-Path -LiteralPath $errorReportPath) {
    Remove-Item -LiteralPath $errorReportPath -Force
}

Write-Host ''
Write-Host "Files scanned: $total"
Write-Host "Flagged extreme cells: $($extremes.Count)"
Write-Host "Read errors: $($readErrorsList.Count)"
Write-Host "Extreme-value report: $reportPath"
if ($readErrorsList.Count -gt 0) { Write-Host "Read-error report: $errorReportPath" -ForegroundColor Yellow }

if ($extremes.Count -gt 0) {
    Write-Host "`nLargest absolute values (review only; do not delete automatically):"
    $extremes |
        Sort-Object { [math]::Abs([double]$_.Value) } -Descending |
        Select-Object -First 20 File, Country, UrbanId, Method, Value |
        Format-Table -AutoSize
} else {
    Write-Host 'No cells crossed the +/-40 review threshold.'
}
