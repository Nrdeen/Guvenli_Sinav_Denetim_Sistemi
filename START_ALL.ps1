# =====================================================
# Complete System Startup Script
# تشغيل النظام الكامل
# =====================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  🎓 EduView - Complete System Startup" -ForegroundColor Green
Write-Host "  تشغيل نظام مراقبة الاختبارات الكامل" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# التحقق من MySQL
Write-Host "🔍 Checking MySQL service..." -ForegroundColor Yellow
$mysqlService = Get-Service -Name "MySQL*" -ErrorAction SilentlyContinue
if ($mysqlService) {
    if ($mysqlService.Status -eq "Running") {
        Write-Host "✅ MySQL is running" -ForegroundColor Green
    } else {
        Write-Host "⚠️  MySQL is installed but not running. Starting..." -ForegroundColor Yellow
        Start-Service $mysqlService.Name
        Write-Host "✅ MySQL started" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  MySQL service not found. Make sure MySQL is installed!" -ForegroundColor Red
    Write-Host "   Download from: https://dev.mysql.com/downloads/mysql/" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Backend Server..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# تشغيل Backend في نافذة جديدة
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .\start_backend.ps1"

Write-Host "⏳ Waiting 5 seconds for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Frontend Application..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# تشغيل Frontend في نافذة جديدة
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .\start_frontend.ps1"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ System Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Access the application at:" -ForegroundColor Cyan
Write-Host "   - Student Login: http://localhost:3000/student-login" -ForegroundColor Yellow
Write-Host "   - Teacher Login: http://localhost:3000/teacher-login" -ForegroundColor Yellow
Write-Host "   - Dashboard: http://localhost:3000/dashboard" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔧 Backend API running at: http://localhost:8001" -ForegroundColor Cyan
Write-Host ""
Write-Host "📖 For more information, see START_HERE.md" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")