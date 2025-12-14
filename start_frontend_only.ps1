# Start only the frontend
Write-Host "Starting Frontend only..." -ForegroundColor Green

# Set Node memory limit
$env:NODE_OPTIONS="--max-old-space-size=4096"
$env:FRONTEND_PORT="3000"

Write-Host "Frontend will run on port 3000" -ForegroundColor Cyan
Write-Host "Make sure backend is running on port 8000!" -ForegroundColor Yellow

reflex run --frontend-only