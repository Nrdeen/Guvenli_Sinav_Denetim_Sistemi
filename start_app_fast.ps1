# Script to start Reflex app with optimized settings
# This helps avoid the 92% freeze issue

Write-Host "Starting Reflex with optimized settings..." -ForegroundColor Green

# Set environment variables to speed up compilation
$env:NODE_OPTIONS="--max-old-space-size=4096"
$env:REFLEX_COMPILE_TIMEOUT="300"

# Clear any stuck processes
Write-Host "Checking for stuck processes..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process -Name "bun" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Start Reflex
Write-Host "Starting Reflex..." -ForegroundColor Cyan
reflex run

# If it fails, try with production mode
if ($LASTEXITCODE -ne 0) {
    Write-Host "Retrying with production mode..." -ForegroundColor Yellow
    reflex run --env prod
}