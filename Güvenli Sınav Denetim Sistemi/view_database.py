"""
أداة لعرض بيانات قاعدة البيانات
Database Viewer Tool

هذا السكريبت يعرض:
- قائمة الأساتذة
- قائمة الاختبارات
- قائمة الطلاب
- تسجيلات الطلاب في الاختبارات
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# إضافة المسار للوصول إلى الموديلات
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import Base, get_db, engine
import models

def print_separator(title=""):
    """طباعة فاصل مع عنوان"""
    print("\n" + "="*80)
    if title:
        print(f"  {title}")
        print("="*80)

def view_teachers():
    """عرض قائمة الأساتذة"""
    print_separator("👨‍🏫 قائمة الأساتذة / Teachers List")
    
    db = next(get_db())
    try:
        teachers = db.query(models.Teacher).all()
        
        if not teachers:
            print("❌ لا يوجد أساتذة في قاعدة البيانات")
            return
        
        print(f"\n✅ عدد الأساتذة: {len(teachers)}\n")
        
        for teacher in teachers:
            print(f"📌 ID: {teacher.id}")
            print(f"   👤 الاسم: {teacher.full_name}")
            print(f"   🔑 اسم المستخدم: {teacher.username}")
            print(f"   📧 البريد: {teacher.email}")
            print(f"   📅 تاريخ التسجيل: {teacher.created_at}")
            print(f"   📝 عدد الاختبارات: {len(teacher.exams)}")
            print("-" * 80)
    finally:
        db.close()

def view_exams():
    """عرض قائمة الاختبارات"""
    print_separator("📝 قائمة الاختبارات / Exams List")
    
    db = next(get_db())
    try:
        exams = db.query(models.Exam).all()
        
        if not exams:
            print("❌ لا يوجد اختبارات في قاعدة البيانات")
            return
        
        print(f"\n✅ عدد الاختبارات: {len(exams)}\n")
        
        for exam in exams:
            print(f"📌 ID: {exam.id}")
            print(f"   📝 اسم الاختبار: {exam.exam_name}")
            print(f"   🔢 رمز الاختبار: {exam.exam_code}")
            print(f"   👨‍🏫 الأستاذ: {exam.teacher.full_name if exam.teacher else 'غير محدد'}")
            print(f"   🕐 وقت البدء: {exam.start_time}")
            print(f"   🕐 وقت الانتهاء: {exam.end_time}")
            print(f"   ⏱️ المدة: {exam.duration_minutes} دقيقة")
            print(f"   📊 الحالة: {exam.status}")
            print(f"   👥 عدد الطلاب المسجلين: {len(exam.registrations)}")
            print(f"   📅 تاريخ الإنشاء: {exam.created_at}")
            print("-" * 80)
    finally:
        db.close()

def view_students():
    """عرض قائمة الطلاب"""
    print_separator("👨‍🎓 قائمة الطلاب / Students List")
    
    db = next(get_db())
    try:
        students = db.query(models.Student).all()
        
        if not students:
            print("❌ لا يوجد طلاب في قاعدة البيانات")
            return
        
        print(f"\n✅ عدد الطلاب: {len(students)}\n")
        
        for student in students:
            print(f"📌 ID: {student.id}")
            print(f"   🆔 رقم الطالب: {student.student_id}")
            print(f"   👤 الاسم: {student.full_name}")
            print(f"   📧 البريد: {student.email}")
            print(f"   📝 عدد الاختبارات المسجل فيها: {len(student.registrations)}")
            print(f"   📅 تاريخ التسجيل: {student.created_at}")
            print("-" * 80)
    finally:
        db.close()

def view_registrations():
    """عرض تسجيلات الطلاب في الاختبارات"""
    print_separator("📋 تسجيلات الطلاب في الاختبارات / Exam Registrations")
    
    db = next(get_db())
    try:
        registrations = db.query(models.ExamRegistration).all()
        
        if not registrations:
            print("❌ لا يوجد تسجيلات")
            return
        
        print(f"\n✅ عدد التسجيلات: {len(registrations)}\n")
        
        # تجميع حسب الاختبار
        exams_dict = {}
        for reg in registrations:
            exam_code = reg.exam.exam_code
            if exam_code not in exams_dict:
                exams_dict[exam_code] = {
                    'exam_name': reg.exam.exam_name,
                    'students': []
                }
            exams_dict[exam_code]['students'].append({
                'student_id': reg.student.student_id,
                'name': reg.student.full_name,
                'status': reg.status,
                'registered_at': reg.registered_at
            })
        
        for exam_code, data in exams_dict.items():
            print(f"\n📝 اختبار: {data['exam_name']} ({exam_code})")
            print(f"   👥 عدد الطلاب: {len(data['students'])}\n")
            
            for idx, student in enumerate(data['students'], 1):
                print(f"   {idx}. {student['name']} ({student['student_id']})")
                print(f"      📊 الحالة: {student['status']}")
                print(f"      📅 تاريخ التسجيل: {student['registered_at']}")
            
            print("-" * 80)
    finally:
        db.close()

def view_active_sessions():
    """عرض الجلسات النشطة"""
    print_separator("🟢 الجلسات النشطة / Active Sessions")
    
    db = next(get_db())
    try:
        sessions = db.query(models.ActiveSession).filter(
            models.ActiveSession.is_active == True
        ).all()
        
        if not sessions:
            print("❌ لا يوجد جلسات نشطة حالياً")
            return
        
        print(f"\n✅ عدد الجلسات النشطة: {len(sessions)}\n")
        
        for session in sessions:
            print(f"📌 Session ID: {session.id}")
            print(f"   👤 الطالب: {session.student.full_name} ({session.student.student_id})")
            print(f"   📝 الاختبار: {session.exam.exam_name}")
            print(f"   🕐 بدء الجلسة: {session.session_start}")
            print(f"   💓 آخر نبضة: {session.last_heartbeat}")
            print(f"   🌐 IP: {session.ip_address}")
            print("-" * 80)
    finally:
        db.close()

def view_violations():
    """عرض الانتهاكات"""
    print_separator("⚠️ الانتهاكات / Violations")
    
    db = next(get_db())
    try:
        violations = db.query(models.Violation).order_by(
            models.Violation.timestamp.desc()
        ).limit(20).all()
        
        if not violations:
            print("✅ لا يوجد انتهاكات مسجلة")
            return
        
        print(f"\n⚠️ آخر 20 انتهاك:\n")
        
        for violation in violations:
            print(f"📌 ID: {violation.id}")
            print(f"   👤 الطالب: {violation.student.full_name}")
            print(f"   📝 الاختبار: {violation.exam.exam_name}")
            print(f"   🚨 نوع الانتهاك: {violation.violation_type}")
            print(f"   ⚡ الخطورة: {violation.severity}")
            print(f"   📝 الوصف: {violation.description}")
            print(f"   🎯 نسبة الثقة: {violation.confidence_score}")
            print(f"   🕐 الوقت: {violation.timestamp}")
            print("-" * 80)
    finally:
        db.close()

def main_menu():
    """القائمة الرئيسية"""
    while True:
        print("\n" + "="*80)
        print("  🗄️ عارض قاعدة البيانات / Database Viewer")
        print("="*80)
        print("\nاختر ما تريد عرضه:")
        print("  1️⃣  - عرض الأساتذة (Teachers)")
        print("  2️⃣  - عرض الاختبارات (Exams)")
        print("  3️⃣  - عرض الطلاب (Students)")
        print("  4️⃣  - عرض التسجيلات (Registrations)")
        print("  5️⃣  - عرض الجلسات النشطة (Active Sessions)")
        print("  6️⃣  - عرض الانتهاكات (Violations)")
        print("  7️⃣  - عرض الكل (Show All)")
        print("  0️⃣  - خروج (Exit)")
        print("-" * 80)
        
        choice = input("\nأدخل اختيارك: ").strip()
        
        if choice == "1":
            view_teachers()
        elif choice == "2":
            view_exams()
        elif choice == "3":
            view_students()
        elif choice == "4":
            view_registrations()
        elif choice == "5":
            view_active_sessions()
        elif choice == "6":
            view_violations()
        elif choice == "7":
            view_teachers()
            view_exams()
            view_students()
            view_registrations()
            view_active_sessions()
            view_violations()
        elif choice == "0":
            print("\n👋 إلى اللقاء!")
            break
        else:
            print("\n❌ اختيار غير صحيح! حاول مرة أخرى.")
        
        input("\n📌 اضغط Enter للمتابعة...")

if __name__ == "__main__":
    try:
        print("\n🚀 جاري الاتصال بقاعدة البيانات...")
        # التحقق من وجود قاعدة البيانات
        if not os.path.exists("backend/exam_monitoring.db"):
            print("❌ قاعدة البيانات غير موجودة!")
            print("💡 قم بتشغيل الخادم أولاً لإنشاء قاعدة البيانات")
            sys.exit(1)
        
        print("✅ تم الاتصال بنجاح!\n")
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 تم الإيقاف بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ: {str(e)}")
        import traceback
        traceback.print_exc()