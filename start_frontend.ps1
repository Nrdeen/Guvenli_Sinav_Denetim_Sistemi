# =====================================================
# Frontend (Reflex) Startup Script
# نص تشغيل واجهة المستخدم
# =====================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  EduView - Frontend Application" -ForegroundColor Green
Write-Host "  واجهة نظام مراقبة الاختبارات" -ForegroundColor Green
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

Write-Host ""

# تثبيت المكتبات إذا لم تكن مثبتة
Write-Host "📦 Installing required packages..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "✅ Packages installed successfully" -ForegroundColor Green
Write-Host ""

# تشغيل تطبيق Reflex
Write-Host "🚀 Starting Reflex Application..." -ForegroundColor Green
Write-Host "   Frontend will be available at:" -ForegroundColor Cyan
Write-Host "   - Student Login: http://localhost:3000/student-login" -ForegroundColor Yellow
Write-Host "   - Teacher Login: http://localhost:3000/teacher-login" -ForegroundColor Yellow
Write-Host "   - Dashboard: http://localhost:3000/dashboard" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

reflex run