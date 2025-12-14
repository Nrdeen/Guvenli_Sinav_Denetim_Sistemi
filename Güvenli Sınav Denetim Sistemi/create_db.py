"""
سكريبت إنشاء قاعدة البيانات SQLite
"""
from backend.database import engine, Base
import backend.models

# إنشاء جميع الجداول
print("إنشاء قاعدة البيانات والجداول...")
Base.metadata.create_all(bind=engine)
print("✅ تم إنشاء قاعدة البيانات بنجاح!")

# إضافة بيانات تجريبية
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from datetime import datetime, timedelta

db = SessionLocal()
try:
    # إضافة معلم
    teacher = backend.models.Teacher(
        username="admin",
        password_hash="admin123",
        full_name="المعلم الافتراضي",
        email="admin@example.com"
    )
    db.add(teacher)
    db.commit()

    # إضافة طلاب
    students_data = [
        ("STU001", "أحمد محمد", "ahmed@example.com"),
        ("STU002", "فاطمة علي", "fatima@example.com"),
        ("STU003", "محمد حسن", "mohamed@example.com"),
        ("STU004", "سارة أحمد", "sara@example.com"),
        ("STU005", "علي محمود", "ali@example.com")
    ]

    for student_id, name, email in students_data:
        student = backend.models.Student(
            student_id=student_id,
            full_name=name,
            email=email
        )
        db.add(student)

    db.commit()

    # إضافة اختبار
    exam = backend.models.Exam(
        teacher_id=1,
        exam_name="اختبار الرياضيات النهائي",
        exam_code="MATH2025",
        start_time=datetime.now() + timedelta(days=1),
        end_time=datetime.now() + timedelta(days=1, hours=2),
        duration_minutes=120,
        status="scheduled"
    )
    db.add(exam)
    db.commit()

    # تسجيل الطلاب في الاختبار
    for i in range(1, 6):
        registration = backend.models.ExamRegistration(
            exam_id=1,
            student_id=i,
            status="registered"
        )
        db.add(registration)

    db.commit()

    print("✅ تم إضافة البيانات التجريبية!")

finally:
    db.close()

print("🎉 قاعدة البيانات جاهزة للاستخدام!")