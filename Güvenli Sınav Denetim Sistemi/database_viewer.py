"""
عارض تفاعلي لقاعدة البيانات SQLite
Interactive SQLite Database Viewer
"""
import sqlite3
import os

DB_PATH = "backend/sinav_guvenlik.db"

def connect_db():
    """الاتصال بقاعدة البيانات"""
    if not os.path.exists(DB_PATH):
        print(f"❌ قاعدة البيانات غير موجودة في: {DB_PATH}")
        return None

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return None

def view_teachers():
    """عرض الأساتذة"""
    print("\n👨‍🏫 الأساتذة / Teachers")

    conn = connect_db()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, full_name, email, created_at FROM teachers")
        teachers = cursor.fetchall()

        if not teachers:
            print("❌ لا يوجد أساتذة")
            return

        print(f"✅ عدد الأساتذة: {len(teachers)}\n")

        for teacher in teachers:
            print(f"ID: {teacher['id']}")
            print(f"اسم المستخدم: {teacher['username']}")
            print(f"الاسم الكامل: {teacher['full_name']}")
            print(f"البريد الإلكتروني: {teacher['email']}")
            print(f"تاريخ التسجيل: {teacher['created_at']}")
            print("-" * 40)

    finally:
        conn.close()

def view_students():
    """عرض الطلاب"""
    print("\n👨‍🎓 الطلاب / Students")

    conn = connect_db()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, student_id, full_name, email, created_at FROM students")
        students = cursor.fetchall()

        if not students:
            print("❌ لا يوجد طلاب")
            return

        print(f"✅ عدد الطلاب: {len(students)}\n")

        for student in students:
            print(f"ID: {student['id']}")
            print(f"رقم الطالب: {student['student_id']}")
            print(f"الاسم الكامل: {student['full_name']}")
            print(f"البريد الإلكتروني: {student['email']}")
            print(f"تاريخ التسجيل: {student['created_at']}")
            print("-" * 40)

    finally:
        conn.close()

def view_exams():
    """عرض الاختبارات"""
    print("\n📝 الاختبارات / Exams")

    conn = connect_db()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.id, e.exam_name, e.exam_code, e.start_time, e.end_time,
                   e.duration_minutes, e.status, e.exam_url, e.exam_instructions,
                   t.full_name as teacher_name
            FROM exams e
            LEFT JOIN teachers t ON e.teacher_id = t.id
        """)
        exams = cursor.fetchall()

        if not exams:
            print("❌ لا يوجد اختبارات")
            return

        print(f"✅ عدد الاختبارات: {len(exams)}\n")

        for exam in exams:
            print(f"ID: {exam['id']}")
            print(f"اسم الاختبار: {exam['exam_name']}")
            print(f"رمز الاختبار: {exam['exam_code']}")
            print(f"الأستاذ: {exam['teacher_name']}")
            print(f"وقت البدء: {exam['start_time']}")
            print(f"وقت الانتهاء: {exam['end_time']}")
            print(f"المدة (دقائق): {exam['duration_minutes']}")
            print(f"الحالة: {exam['status']}")
            if exam['exam_url']:
                print(f"رابط الاختبار: {exam['exam_url']}")
            if exam['exam_instructions']:
                print(f"تعليمات الاختبار: {exam['exam_instructions']}")
            
            # عرض الطلاب المسجلين
            cursor2 = conn.cursor()
            cursor2.execute("""
                SELECT s.student_id, s.full_name
                FROM exam_registrations er
                JOIN students s ON er.student_id = s.id
                WHERE er.exam_id = ?
            """, (exam['id'],))
            registered_students = cursor2.fetchall()
            
            if registered_students:
                print(f"الطلاب المسجلين ({len(registered_students)}):")
                for student in registered_students:
                    print(f"  - {student['full_name']} ({student['student_id']})")
            else:
                print("لا يوجد طلاب مسجلين")
            
            print("-" * 40)

    finally:
        conn.close()

def view_registrations():
    """عرض التسجيلات"""
    print("\n📋 التسجيلات / Registrations")

    conn = connect_db()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT er.id, er.registered_at, er.status,
                   s.student_id, s.full_name as student_name,
                   e.exam_name, e.exam_code
            FROM exam_registrations er
            JOIN students s ON er.student_id = s.id
            JOIN exams e ON er.exam_id = e.id
        """)
        registrations = cursor.fetchall()

        if not registrations:
            print("❌ لا يوجد تسجيلات")
            return

        print(f"✅ عدد التسجيلات: {len(registrations)}\n")

        for reg in registrations:
            print(f"ID: {reg['id']}")
            print(f"الطالب: {reg['student_name']} ({reg['student_id']})")
            print(f"الاختبار: {reg['exam_name']} ({reg['exam_code']})")
            print(f"تاريخ التسجيل: {reg['registered_at']}")
            print(f"الحالة: {reg['status']}")
            print("-" * 40)

    finally:
        conn.close()

def view_sessions():
    """عرض الجلسات النشطة"""
    print("\n🖥️ الجلسات النشطة / Active Sessions")

    conn = connect_db()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, s.session_start, s.last_heartbeat, s.ip_address,
                   s.is_active, st.student_id, st.full_name as student_name,
                   e.exam_name
            FROM active_sessions s
            JOIN students st ON s.student_id = st.id
            JOIN exams e ON s.exam_id = e.id
        """)
        sessions = cursor.fetchall()

        if not sessions:
            print("❌ لا يوجد جلسات نشطة")
            return

        print(f"✅ عدد الجلسات: {len(sessions)}\n")

        for session in sessions:
            print(f"ID: {session['id']}")
            print(f"الطالب: {session['student_name']} ({session['student_id']})")
            print(f"الاختبار: {session['exam_name']}")
            print(f"بداية الجلسة: {session['session_start']}")
            print(f"آخر نبضة: {session['last_heartbeat']}")
            print(f"عنوان IP: {session['ip_address']}")
            print(f"نشط: {'نعم' if session['is_active'] else 'لا'}")
            print("-" * 40)

    finally:
        conn.close()

def view_violations():
    """عرض الانتهاكات"""
    print("\n⚠️ الانتهاكات / Violations")

    conn = connect_db()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.id, v.violation_type, v.severity, v.description,
                   v.confidence_score, v.timestamp, s.student_id,
                   s.full_name as student_name, e.exam_name
            FROM violations v
            JOIN students s ON v.student_id = s.id
            JOIN exams e ON v.exam_id = e.id
        """)
        violations = cursor.fetchall()

        if not violations:
            print("❌ لا يوجد انتهاكات")
            return

        print(f"✅ عدد الانتهاكات: {len(violations)}\n")

        for violation in violations:
            print(f"ID: {violation['id']}")
            print(f"الطالب: {violation['student_name']} ({violation['student_id']})")
            print(f"الاختبار: {violation['exam_name']}")
            print(f"نوع الانتهاك: {violation['violation_type']}")
            print(f"الشدة: {violation['severity']}")
            print(f"الوصف: {violation['description']}")
            print(f"درجة الثقة: {violation['confidence_score']}")
            print(f"الوقت: {violation['timestamp']}")
            print("-" * 40)

    finally:
        conn.close()

def show_menu():
    """عرض القائمة"""
    while True:
        print("\n" + "="*60)
        print("🎓 عارض قاعدة البيانات - EduView Database Viewer")
        print("="*60)
        print("اختر ما تريد عرضه:")
        print("  1️⃣  - عرض الأساتذة (Teachers)")
        print("  2️⃣  - عرض الاختبارات (Exams)")
        print("  3️⃣  - عرض الطلاب (Students)")
        print("  4️⃣  - عرض التسجيلات (Registrations)")
        print("  5️⃣  - عرض الجلسات النشطة (Active Sessions)")
        print("  6️⃣  - عرض الانتهاكات (Violations)")
        print("  7️⃣  - عرض الكل (Show All)")
        print("  0️⃣  - خروج (Exit)")
        print("="*60)

        try:
            choice = input("اختر رقم (0-7): ").strip()

            if choice == "0":
                print("👋 شكراً لاستخدام العارض!")
                break
            elif choice == "1":
                view_teachers()
            elif choice == "2":
                view_exams()
            elif choice == "3":
                view_students()
            elif choice == "4":
                view_registrations()
            elif choice == "5":
                view_sessions()
            elif choice == "6":
                view_violations()
            elif choice == "7":
                view_teachers()
                view_exams()
                view_students()
                view_registrations()
                view_sessions()
                view_violations()
            else:
                print("❌ اختيار غير صحيح، يرجى المحاولة مرة أخرى")

            input("\nاضغط Enter للمتابعة...")

        except KeyboardInterrupt:
            print("\n👋 تم الخروج!")
            break
        except Exception as e:
            print(f"❌ خطأ: {e}")
            input("اضغط Enter للمتابعة...")

if __name__ == "__main__":
    show_menu()