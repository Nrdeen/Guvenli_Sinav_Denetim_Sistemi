"""
عارض بسيط لقاعدة البيانات SQLite
Simple SQLite Database Viewer

أداة بسيطة لعرض محتويات قاعدة البيانات بدون الحاجة لـ SQLAlchemy
"""

import sqlite3
import os
from datetime import datetime
from tabulate import tabulate

DB_PATH = "backend/exam_monitoring.db"

def connect_db():
    """الاتصال بقاعدة البيانات"""
    if not os.path.exists(DB_PATH):
        print(f"❌ قاعدة البيانات غير موجودة في: {DB_PATH}")
        print("💡 قم بتشغيل الخادم أولاً لإنشاء قاعدة البيانات")
        return None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # للوصول للأعمدة بالاسم
        return conn
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return None

def print_separator(title=""):
    """طباعة فاصل"""
    print("\n" + "="*100)
    if title:
        print(f"  {title}")
        print("="*100)

def view_teachers():
    """عرض الأساتذة"""
    print_separator("👨‍🏫 الأساتذة / Teachers")
    
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teachers")
        teachers = cursor.fetchall()
        
        if not teachers:
            print("\n❌ لا يوجد أساتذة")
            return
        
        print(f"\n✅ عدد الأساتذة: {len(teachers)}\n")
        
        # تحضير البيانات للجدول
        headers = ["ID", "اسم المستخدم", "الاسم الكامل", "البريد الإلكتروني", "تاريخ التسجيل"]
        data = []
        
        for teacher in teachers:
            data.append([
                teacher['id'],
                teacher['username'],
                teacher['full_name'],
                teacher['email'],
                teacher['created_at']
            ])
        
        print(tabulate(data, headers=headers, tablefmt="grid"))
        
    finally:
        conn.close()

def view_exams():
    """عرض الاختبارات"""
    print_separator("📝 الاختبارات / Exams")
    
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.*, t.full_name as teacher_name,
                   (SELECT COUNT(*) FROM exam_registrations WHERE exam_id = e.id) as student_count
            FROM exams e
            LEFT JOIN teachers t ON e.teacher_id = t.id
        """)
        exams = cursor.fetchall()
        
        if not exams:
            print("\n❌ لا يوجد اختبارات")
            return
        
        print(f"\n✅ عدد الاختبارات: {len(exams)}\n")
        
        headers = ["ID", "اسم الاختبار", "الرمز", "الأستاذ", "وقت البدء", "المدة", "الحالة", "عدد الطلاب"]
        data = []
        
        for exam in exams:
            data.append([
                exam['id'],
                exam['exam_name'],
                exam['exam_code'],
                exam['teacher_name'],
                exam['start_time'],
                f"{exam['duration_minutes']} دقيقة",
                exam['status'],
                exam['student_count']
            ])
        
        print(tabulate(data, headers=headers, tablefmt="grid"))
        
    finally:
        conn.close()

def view_students():
    """عرض الطلاب"""
    print_separator("👨‍🎓 الطلاب / Students")
    
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.*,
                   (SELECT COUNT(*) FROM exam_registrations WHERE student_id = s.id) as exam_count
            FROM students s
        """)
        students = cursor.fetchall()
        
        if not students:
            print("\n❌ لا يوجد طلاب")
            return
        
        print(f"\n✅ عدد الطلاب: {len(students)}\n")
        
        headers = ["ID", "رقم الطالب", "الاسم الكامل", "البريد الإلكتروني", "عدد الاختبارات", "تاريخ التسجيل"]
        data = []
        
        for student in students:
            data.append([
                student['id'],
                student['student_id'],
                student['full_name'],
                student['email'],
                student['exam_count'],
                student['created_at']
            ])
        
        print(tabulate(data, headers=headers, tablefmt="grid"))
        
    finally:
        conn.close()

def view_registrations():
    """عرض التسجيلات"""
    print_separator("📋 التسجيلات / Registrations")
    
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                er.id,
                e.exam_name,
                e.exam_code,
                s.student_id,
                s.full_name,
                er.status,
                er.registered_at
            FROM exam_registrations er
            JOIN exams e ON er.exam_id = e.id
            JOIN students s ON er.student_id = s.id
            ORDER BY e.exam_code, s.student_id
        """)
        registrations = cursor.fetchall()
        
        if not registrations:
            print("\n❌ لا يوجد تسجيلات")
            return
        
        print(f"\n✅ عدد التسجيلات: {len(registrations)}\n")
        
        headers = ["ID", "الاختبار", "الرمز", "رقم الطالب", "اسم الطالب", "الحالة", "تاريخ التسجيل"]
        data = []
        
        for reg in registrations:
            data.append([
                reg['id'],
                reg['exam_name'],
                reg['exam_code'],
                reg['student_id'],
                reg['full_name'],
                reg['status'],
                reg['registered_at']
            ])
        
        print(tabulate(data, headers=headers, tablefmt="grid"))
        
    finally:
        conn.close()

def view_active_sessions():
    """عرض الجلسات النشطة"""
    print_separator("🟢 الجلسات النشطة / Active Sessions")
    
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                a.id,
                s.student_id,
                s.full_name,
                e.exam_name,
                e.exam_code,
                a.session_start,
                a.last_heartbeat,
                a.ip_address
            FROM active_sessions a
            JOIN students s ON a.student_id = s.id
            JOIN exams e ON a.exam_id = e.id
            WHERE a.is_active = 1
            ORDER BY a.last_heartbeat DESC
        """)
        sessions = cursor.fetchall()
        
        if not sessions:
            print("\n✅ لا يوجد جلسات نشطة حالياً")
            return
        
        print(f"\n🟢 عدد الجلسات النشطة: {len(sessions)}\n")
        
        headers = ["Session ID", "رقم الطالب", "اسم الطالب", "الاختبار", "بدء الجلسة", "آخر نبضة", "IP"]
        data = []
        
        for session in sessions:
            data.append([
                session['id'],
                session['student_id'],
                session['full_name'],
                f"{session['exam_name']}\n({session['exam_code']})",
                session['session_start'],
                session['last_heartbeat'],
                session['ip_address']
            ])
        
        print(tabulate(data, headers=headers, tablefmt="grid"))
        
    finally:
        conn.close()

def view_violations_summary():
    """عرض ملخص الانتهاكات"""
    print_separator("⚠️ ملخص الانتهاكات / Violations Summary")
    
    conn = connect_db()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # إجمالي الانتهاكات
        cursor.execute("SELECT COUNT(*) as total FROM violations")
        total = cursor.fetchone()['total']
        
        if total == 0:
            print("\n✅ لا يوجد انتهاكات مسجلة")
            return
        
        print(f"\n⚠️ إجمالي الانتهاكات: {total}\n")
        
        # حسب النوع
        print("📊 حسب النوع:")
        cursor.execute("""
            SELECT violation_type, COUNT(*) as count
            FROM violations
            GROUP BY violation_type
            ORDER BY count DESC
        """)
        type_stats = cursor.fetchall()
        
        headers = ["نوع الانتهاك", "العدد"]
        data = [[row['violation_type'], row['count']] for row in type_stats]
        print(tabulate(data, headers=headers, tablefmt="grid"))
        
        # حسب الخطورة
        print("\n⚡ حسب الخطورة:")
        cursor.execute("""
            SELECT severity, COUNT(*) as count
            FROM violations
            GROUP BY severity
            ORDER BY 
                CASE severity
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                END
        """)
        severity_stats = cursor.fetchall()
        
        headers = ["الخطورة", "العدد"]
        data = [[row['severity'], row['count']] for row in severity_stats]
        print(tabulate(data, headers=headers, tablefmt="grid"))
        
        # أكثر الطلاب انتهاكاً
        print("\n👤 أكثر 5 طلاب انتهاكاً:")
        cursor.execute("""
            SELECT 
                s.student_id,
                s.full_name,
                COUNT(*) as violation_count
            FROM violations v
            JOIN students s ON v.student_id = s.id
            GROUP BY v.student_id
            ORDER BY violation_count DESC
            LIMIT 5
        """)
        top_violators = cursor.fetchall()
        
        headers = ["رقم الطالب", "الاسم", "عدد الانتهاكات"]
        data = [[row['student_id'], row['full_name'], row['violation_count']] for row in top_violators]
        print(tabulate(data, headers=headers, tablefmt="grid"))
        
    finally:
        conn.close()

def export_to_excel():
    """تصدير البيانات إلى Excel"""
    print_separator("📊 تصدير إلى Excel / Export to Excel")
    
    try:
        import pandas as pd
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        
        conn = connect_db()
        if not conn:
            return
        
        # إنشاء ملف Excel
        filename = f"database_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # تصدير كل جدول
            tables = ['teachers', 'exams', 'students', 'exam_registrations', 'active_sessions', 'violations']
            
            for table in tables:
                df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                df.to_excel(writer, sheet_name=table, index=False)
        
        conn.close()
        
        print(f"\n✅ تم التصدير بنجاح إلى: {filename}")
        
    except ImportError:
        print("\n❌ يجب تثبيت pandas و openpyxl أولاً:")
        print("   pip install pandas openpyxl")
    except Exception as e:
        print(f"\n❌ خطأ في التصدير: {e}")

def main_menu():
    """القائمة الرئيسية"""
    while True:
        print("\n" + "="*100)
        print("  🗄️ عارض قاعدة البيانات البسيط / Simple Database Viewer")
        print("="*100)
        print("\nاختر ما تريد عرضه:")
        print("  1️⃣  - الأساتذة (Teachers)")
        print("  2️⃣  - الاختبارات (Exams)")
        print("  3️⃣  - الطلاب (Students)")
        print("  4️⃣  - التسجيلات (Registrations)")
        print("  5️⃣  - الجلسات النشطة (Active Sessions)")
        print("  6️⃣  - ملخص الانتهاكات (Violations Summary)")
        print("  7️⃣  - عرض الكل (Show All)")
        print("  8️⃣  - تصدير إلى Excel (Export to Excel)")
        print("  0️⃣  - خروج (Exit)")
        print("-" * 100)
        
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
            view_violations_summary()
        elif choice == "7":
            view_teachers()
            view_exams()
            view_students()
            view_registrations()
            view_active_sessions()
            view_violations_summary()
        elif choice == "8":
            export_to_excel()
        elif choice == "0":
            print("\n👋 إلى اللقاء!")
            break
        else:
            print("\n❌ اختيار غير صحيح!")
        
        input("\n📌 اضغط Enter للمتابعة...")

if __name__ == "__main__":
    try:
        # التحقق من تثبيت tabulate
        try:
            from tabulate import tabulate
        except ImportError:
            print("❌ يجب تثبيت مكتبة tabulate أولاً:")
            print("   pip install tabulate")
            exit(1)
        
        print("\n🚀 جاري الاتصال بقاعدة البيانات...")
        
        if not os.path.exists(DB_PATH):
            print(f"❌ قاعدة البيانات غير موجودة في: {DB_PATH}")
            print("💡 قم بتشغيل الخادم أولاً لإنشاء قاعدة البيانات")
            exit(1)
        
        print("✅ تم الاتصال بنجاح!\n")
        main_menu()
        
    except KeyboardInterrupt:
        print("\n\n👋 تم الإيقاف بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()