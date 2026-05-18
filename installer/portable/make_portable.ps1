# Builds a portable LocalForge bundle: zip the release build, add a
# `portable.txt` marker that signals the Rust shell to keep all data
# next to the executable (no registry writes, no APPDATA usage).
#
# v1.1.0: Pre-bootstraps the DirectML image backend. Video Pro (ZLUDA)
# is left as an in-app install so the portable zip stays a reasonable
# size (~7 GB instead of ~13 GB).

param(
  [string]$ReleaseDir = "..\..\src-tauri\target\release",
  [string]$OutDir     = ".\dist",
  [string]$Version    = "1.1.0",
  [switch]$IncludeVideoPro
)
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force $OutDir | Out-Null

$bundle = Join-Path $OutDir "LocalForge-$Version-portable"
if (Test-Path $bundle) { Remove-Item -Recurse -Force $bundle }
New-Item -ItemType Directory $bundle | Out-Null

Write-Host "Building portable LocalForge $Version..." -ForegroundColor Cyan

# 1. Copy Tauri executable
Copy-Item "$ReleaseDir\LocalForge.exe" $bundle

# 2. Bundle Python backend
Copy-Item -Recurse "..\..\backend" "$bundle\backend"

# 3. Resources / icons
Copy-Item -Recurse "..\..\resources" "$bundle\resources"

# 4. Portable marker — Rust shell looks for this to switch to portable mode
Set-Content "$bundle\portable.txt" @"
LocalForge runs in portable mode when this file exists.
All user data (models, outputs, settings) lives in ./localforge_data/
next to LocalForge.exe instead of %APPDATA%\LocalForge.
"@

# 5. Pre-create data dir so first launch is instant
New-Item -ItemType Directory -Force "$bundle\localforge_data" | Out-Null
New-Item -ItemType Directory -Force "$bundle\localforge_data\models" | Out-Null
New-Item -ItemType Directory -Force "$bundle\localforge_data\outputs" | Out-Null

# 6. Pre-bootstrap the image backend (saves users 5-10 min on first run)
Write-Host "Pre-bootstrapping image backend (DirectML)..." -ForegroundColor Cyan
$env:LOCALFORGE_DATA_DIR = "$bundle\localforge_data"
& "$bundle\backend\python\python.exe" "$bundle\backend\scripts\bootstrap.py"

# 7. Optionally include Video Pro (adds ~6 GB)
if ($IncludeVideoPro) {
  Write-Host "Installing Video Pro backend (ZLUDA)..." -ForegroundColor Cyan
  & "$bundle\backend\python\python.exe" "$bundle\backend\scripts\install_video_pro.py"
}

# 8. Quick-start README in the bundle
Set-Content "$bundle\README.txt" @"
LocalForge $Version — Portable
================================

Just double-click LocalForge.exe.

Everything (models, outputs, settings) lives in ./localforge_data/.
You can move this entire folder to a USB drive or another PC.

Image generation works out of the box.
For photoreal video (LTX-Video, Wan 2.1, Hunyuan), open the Video Pro tab
in the app and click Install. That downloads ~6 GB the first time only.

No cloud. No login. No telemetry.
"@

# 9. Zip it
$zip = "$bundle.zip"
if (Test-Path $zip) { Remove-Item $zip }
Write-Host "Compressing to $zip..." -ForegroundColor Cyan
Compress-Archive -Path "$bundle\*" -DestinationPath $zip -CompressionLevel Optimal

$size = [math]::Round((Get-Item $zip).Length / 1GB, 2)
Write-Host "Built portable bundle: $zip ($size GB)" -ForegroundColor Green
