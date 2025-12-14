"""
عارض بسيط لقاعدة البيانات SQLite - عرض الطلاب
"""
import sqlite3

DB_PATH = "backend/sinav_guvenlik.db"

def view_students():
    """عرض الطلاب"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, student_id, full_name, email, created_at FROM students")
    students = cursor.fetchall()

    if not students:
        print("❌ لا يوجد طلاب")
        return

    print(f"\n✅ عدد الطلاب: {len(students)}\n")
    print("=" * 80)
    print("الطلاب المسجلون:")
    print("=" * 80)

    for student in students:
        print(f"ID: {student[0]}")
        print(f"رقم الطالب: {student[1]}")
        print(f"الاسم الكامل: {student[2]}")
        print(f"البريد الإلكتروني: {student[3]}")
        print(f"تاريخ التسجيل: {student[4]}")
        print("-" * 40)

    conn.close()

if __name__ == "__main__":
    view_students()