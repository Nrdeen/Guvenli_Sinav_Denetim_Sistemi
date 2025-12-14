# سكريبت لتشغيل النظام بالكامل
# Start Everything Script

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  🚀 تشغيل نظام EduView" -ForegroundColor Cyan
Write-Host "  Starting EduView System" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

Write-Host "`n📍 الخطوة 1: تشغيل Backend..." -ForegroundColor Yellow

# تشغيل Backend في نافذة جديدة
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'Güvenli Sınav Denetim Sistemi' ; python backend/main.py"

Write-Host "✅ تم تشغيل Backend في نافذة جديدة" -ForegroundColor Green
Write-Host "⏳ انتظر 5 ثواني..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "`n📍 الخطوة 2: تشغيل Frontend..." -ForegroundColor Yellow

# تشغيل Frontend في نافذة جديدة
Start-Process powershell -ArgumentList "-NoExit", "-Command", "reflex run"

Write-Host "✅ تم تشغيل Frontend في نافذة جديدة" -ForegroundColor Green

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "  ✅ تم تشغيل النظام بنجاح!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan

Write-Host "`n📝 الروابط المهمة:" -ForegroundColor Yellow
Write-Host "   🏠 الصفحة الرئيسية: http://localhost:3001" -ForegroundColor White
Write-Host "   👨‍🏫 لوحة تحكم المعلم: http://localhost:3001/admin/dashboard" -ForegroundColor White
Write-Host "   👨‍🎓 دخول الطالب: http://localhost:3001/student-login" -ForegroundColor White
Write-Host "   🎥 كشف الغش: http://localhost:3001/detection" -ForegroundColor White

Write-Host "`n⚠️ ملاحظة: لا تغلق هذه النافذة أو النوافذ الأخرى!" -ForegroundColor Red

Write-Host "`n📌 اضغط Enter للخروج من هذه النافذة فقط..."
Read-Host