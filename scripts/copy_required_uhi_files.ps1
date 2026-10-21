[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$Source = ""
)
$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($Source)) {
    $UserProfile = $env:USERPROFILE
    $Candidates = @(
        (Join-Path $UserProfile 'OneDrive\Masaüstü\urban-heat-transfer\data\UHII_dataset'),
        (Join-Path $UserProfile 'OneDrive\Desktop\urban-heat-transfer\data\UHII_dataset'),
        (Join-Path $UserProfile 'Desktop\urban-heat-transfer\data\UHII_dataset')
    )
    $Source = $Candidates | Where-Object { Test-Path -LiteralPath $_ -PathType Container } | Select-Object -First 1
}
if (-not $Source -or -not (Test-Path -LiteralPath $Source -PathType Container)) {
    Write-Host 'Kaynak UHII_dataset klasörü bulunamadı; hiçbir dosya kopyalanmadı.' -ForegroundColor Red
    Write-Host 'Örnek kullanım: .\scripts\copy_required_uhi_files.ps1 -Source "C:\...\urban-heat-transfer\data\UHII_dataset"'
    exit 2
}
$Destination = Join-Path $ProjectRoot 'data\raw\UHII_dataset'
$Expected = foreach ($Year in 2001..2020) { foreach ($Period in 6,7,8,22) { "Mod2_Nig_${Year}_${Period}.csv" } }
$Missing = @($Expected | Where-Object { -not (Test-Path -LiteralPath (Join-Path $Source $_) -PathType Leaf) })
if ($Missing.Count -gt 0) {
    Write-Host "Eksik kaynak dosya var ($($Missing.Count)); hiçbir dosya kopyalanmadı." -ForegroundColor Red
    $Missing | Select-Object -First 30 | ForEach-Object { Write-Host $_ }
    exit 3
}
# Preflight every collision before copying any file to avoid a partial copy on a mismatch.
$Conflicts = @()
foreach ($Name in $Expected) {
    $Src = Join-Path $Source $Name
    $Dst = Join-Path $Destination $Name
    if (Test-Path -LiteralPath $Dst -PathType Leaf) {
        $SrcHash = (Get-FileHash -LiteralPath $Src -Algorithm SHA256).Hash
        $DstHash = (Get-FileHash -LiteralPath $Dst -Algorithm SHA256).Hash
        if ($SrcHash -ne $DstHash) { $Conflicts += $Name }
    }
}
if ($Conflicts.Count -gt 0) {
    Write-Host 'ÇAKIŞMA: hedefte aynı adlı ama farklı içerikli dosyalar var; hiçbir dosya kopyalanmadı.' -ForegroundColor Red
    $Conflicts | ForEach-Object { Write-Host $_ }
    exit 4
}
New-Item -ItemType Directory -Force -Path $Destination | Out-Null
$Copied = 0; $AlreadySame = 0
foreach ($Name in $Expected) {
    $Src = Join-Path $Source $Name
    $Dst = Join-Path $Destination $Name
    if (Test-Path -LiteralPath $Dst -PathType Leaf) { $AlreadySame++ }
    else { Copy-Item -LiteralPath $Src -Destination $Dst; $Copied++ }
}
$DestCount = @($Expected | Where-Object { Test-Path -LiteralPath (Join-Path $Destination $_) -PathType Leaf }).Count
Write-Host "BAŞARILI: $DestCount / 80 doğru kaynak dosyası hazır." -ForegroundColor Green
Write-Host "Yeni kopyalanan: $Copied; zaten birebir aynı olan: $AlreadySame"
Write-Host "Kaynak klasörde hiçbir dosya silinmedi veya yeniden adlandırılmadı."
Write-Host "Hedef: $Destination"
