# 🎓 دليل التشغيل السريع - EduView Exam Monitoring System

## ⚠️ حل مشكلة الاتصال بالخادم

### المشكلة
```
Check if server is reachable at ws://localhost:8001/_event
```

### السبب
الخادم الخلفي (Backend Server) غير مشغّل على المنفذ 8001

---

## 🚀 خطوات التشغيل السريعة

### الخطوة 1️⃣: تشغيل الخادم الخلفي (Backend)

**في PowerShell:**

```powershell
.\start_backend.ps1
```

أو يدوياً:

```powershell
cd "Güvenli Sınav Denetim Sistemi\backend"
python main.py
```

✅ **يجب أن ترى:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001
```

---

### الخطوة 2️⃣: تشغيل الواجهة الأمامية (Frontend)

**في PowerShell جديد:**

```powershell
.\start_frontend.ps1
```

أو يدوياً:

```powershell
reflex run
```

✅ **يجب أن ترى:**
```
App running at: http://localhost:3000
```

---

## 📋 الروابط المهمة

بعد تشغيل كلا الخادمين:

| الصفحة | الرابط |
|--------|--------|
| 🎓 تسجيل دخول الطالب | http://localhost:3000/student-login |
| 👨‍🏫 تسجيل دخول الأستاذ | http://localhost:3000/teacher-login |
| 📊 لوحة المراقبة | http://localhost:3000/dashboard |
| 🏠 الصفحة الرئيسية | http://localhost:3000/ |

---

## 🔧 إعداد قاعدة البيانات (إذا لم تكن جاهزة)

### 1. تثبيت MySQL
- حمّل من: https://dev.mysql.com/downloads/mysql/

### 2. إنشاء قاعدة البيانات

افتح MySQL Command Line:

```sql
CREATE DATABASE sinav_guvenlik_sistemi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. تشغيل ملف Schema

```sql
source "C:\Users\ASUS\Downloads\EduView-main\Güvenli Sınav Denetim Sistemi\database\schema.sql"
```

### 4. تعديل ملف .env

افتح `Güvenli Sınav Denetim Sistemi\backend\.env` وعدّل:

```env
DB_PASSWORD=كلمة_المرور_الخاصة_بك
```

---

## 🧪 بيانات تجريبية للاختبار

### للطلاب:
- رقم الطالب: `STU001`, `STU002`, `STU003`
- رمز الاختبار: `PROG2025`

### للأستاذة:
- Username: `admin`
- Password: `admin123`

---

## ❌ حل المشاكل الشائعة

### مشكلة 1: Backend لا يعمل
```
❌ Error: No module named 'fastapi'
```

**الحل:**
```powershell
cd "Güvenli Sınav Denetim Sistemi\backend"
pip install -r requirements.txt
```

---

### مشكلة 2: قاعدة البيانات لا تتصل
```
❌ Error: Access denied for user 'root'@'localhost'
```

**الحل:**
1. تأكد من تشغيل MySQL
2. تأكد من كلمة المرور في `.env`
3. تأكد من إنشاء قاعدة البيانات

---

### مشكلة 3: Reflex لا يعمل
```
❌ Error: reflex: command not found
```

**الحل:**
```powershell
pip install reflex==0.7.1
```

---

## 📞 تدفق العمل الكامل

```
1. تشغيل Backend (Port 8001) ✅
   ↓
2. تشغيل Frontend (Port 3000) ✅
   ↓
3. الطالب يفتح: http://localhost:3000/student-login
   ↓
4. يدخل رقم الطالب + رمز الاختبار
   ↓
5. يضغط "بدء المراقبة والاختبار"
   ↓
6. تبدأ الكاميرا + نظام الكشف عن الغش ✅
```

---

## 🎯 ملاحظات مهمة

1. ✅ يجب تشغيل **Backend أولاً** ثم Frontend
2. ✅ تأكد من عمل MySQL قبل تشغيل Backend
3. ✅ تأكد من تعديل كلمة المرور في `.env`
4. ✅ Backend يعمل على Port 8001
5. ✅ Frontend يعمل على Port 3000

---

## 🆘 الدعم

إذا واجهت أي مشكلة، تأكد من:
- [ ] MySQL يعمل
- [ ] Backend يعمل على http://localhost:8001
- [ ] Frontend يعمل على http://localhost:3000
- [ ] ملف `.env` محدّث بكلمة المرور الصحيحة
- [ ] جميع المكتبات مثبتة (`pip install -r requirements.txt`)

---

**تم إنشاء هذا الدليل بواسطة Kombai AI Assistant** 🤖