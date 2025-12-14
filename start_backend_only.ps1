# Start only the backend server
Write-Host "Starting Backend only..." -ForegroundColor Green

# Kill any existing processes
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*reflex*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Start backend
$env:LOGLEVEL="debug"
$env:BACKEND_PORT="8000"

Write-Host "Backend will run on port 8000" -ForegroundColor Cyan
reflex run --backend-only