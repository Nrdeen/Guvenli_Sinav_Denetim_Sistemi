# تثبيت المكتبات المطلوبة لعارض قاعدة البيانات
# Install requirements for database viewer

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  تثبيت مكتبات عارض قاعدة البيانات" -ForegroundColor Cyan
Write-Host "  Installing Database Viewer Requirements" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

Write-Host "`n📦 جاري تثبيت المكتبات..." -ForegroundColor Yellow

# تثبيت المكتبات الأساسية
pip install tabulate

Write-Host "`n✅ تم تثبيت المكتبات الأساسية" -ForegroundColor Green

# سؤال عن تثبيت مكتبات Excel
$installExcel = Read-Host "`n❓ هل تريد تثبيت مكتبات التصدير إلى Excel؟ (y/n)"

if ($installExcel -eq "y" -or $installExcel -eq "Y") {
    Write-Host "`n📊 جاري تثبيت مكتبات Excel..." -ForegroundColor Yellow
    pip install pandas openpyxl
    Write-Host "✅ تم تثبيت مكتبات Excel" -ForegroundColor Green
}

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "  ✅ اكتمل التثبيت!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan

Write-Host "`n📝 لتشغيل عارض قاعدة البيانات:" -ForegroundColor Yellow
Write-Host "   python simple_db_viewer.py" -ForegroundColor White

Write-Host "`n📌 اضغط Enter للخروج..."
Read-Host