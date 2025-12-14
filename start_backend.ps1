# =====================================================
# Backend Server Startup Script
# نص تشغيل خادم Backend
# =====================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Güvenli Sınav - Backend Server" -ForegroundColor Green
Write-Host "  خادم نظام مراقبة الاختبارات" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# التحقق من وجود Python
Write-Host "🔍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# الانتقال إلى مجلد Backend
$backendPath = Join-Path $PSScriptRoot "Güvenli Sınav Denetim Sistemi\backend"
Set-Location $backendPath
Write-Host "📂 Changed directory to: $backendPath" -ForegroundColor Cyan
Write-Host ""

# التحقق من ملف .env
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found! Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created. Please edit it with your database password!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Opening .env file for editing..." -ForegroundColor Cyan
    notepad ".env"
    Write-Host ""
    Read-Host "Press Enter after saving your database password in .env file"
}

# تثبيت المكتبات إذا لم تكن مثبتة
Write-Host "📦 Installing required packages..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "✅ Packages installed successfully" -ForegroundColor Green
Write-Host ""

# تشغيل الخادم
Write-Host "🚀 Starting Backend Server on http://localhost:8001" -ForegroundColor Green
Write-Host "   Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

python main.py