import sqlite3
import sys

DB_PATH = "backend/exam_monitoring.db"

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("=" * 60)
    print("قاعدة البيانات - الطلاب المسجلين")
    print("=" * 60)
    
    # Get all students
    cursor.execute("SELECT student_id, full_name, email FROM students")
    students = cursor.fetchall()
    
    if students:
        for student in students:
            print(f"ID: {student[0]}")
            print(f"Name: {student[1]}")
            print(f"Email: {student[2]}")
            print("-" * 40)
        print(f"\nإجمالي الطلاب: {len(students)}")
    else:
        print("لا يوجد طلاب في قاعدة البيانات")
    
    print("\n" + "=" * 60)
    print("الاختبارات المسجلة")
    print("=" * 60)
    
    # Get all exams
    cursor.execute("SELECT exam_code, exam_name FROM exams")
    exams = cursor.fetchall()
    
    if exams:
        for exam in exams:
            print(f"Code: {exam[0]}, Name: {exam[1]}")
            
            # Get registered students for this exam
            cursor.execute("""
                SELECT s.student_id, s.full_name 
                FROM students s
                JOIN exam_registrations er ON s.id = er.student_id
                JOIN exams e ON er.exam_id = e.id
                WHERE e.exam_code = ?
            """, (exam[0],))
            exam_students = cursor.fetchall()
            
            if exam_students:
                print(f"  الطلاب المسجلين ({len(exam_students)}):")
                for st in exam_students:
                    print(f"    - {st[0]}: {st[1]}")
            else:
                print("  لا يوجد طلاب مسجلين")
            print("-" * 40)
    else:
        print("لا توجد اختبارات في قاعدة البيانات")
    
    conn.close()
    
except Exception as e:
    print(f"خطأ: {e}")
    sys.exit(1)