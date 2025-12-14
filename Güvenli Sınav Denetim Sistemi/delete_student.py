"""
أداة لحذف طالب من قاعدة البيانات
Delete Student Tool
"""

import sqlite3
import os
import sys

DB_PATH = "backend/exam_monitoring.db"

def delete_student_by_id(student_id):
    """حذف طالب برقم الطالب"""
    if not os.path.exists(DB_PATH):
        print(f"❌ قاعدة البيانات غير موجودة: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # التحقق من وجود الطالب
        cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            print(f"❌ الطالب {student_id} غير موجود في قاعدة البيانات")
            conn.close()
            return False
        
        print(f"\n📋 بيانات الطالب:")
        print(f"   ID: {student[0]}")
        print(f"   رقم الطالب: {student[1]}")
        print(f"   الاسم: {student[2]}")
        print(f"   البريد: {student[3]}")
        
        # تأكيد الحذف
        confirm = input(f"\n⚠️ هل أنت متأكد من حذف الطالب {student_id}؟ (yes/no): ").strip().lower()
        
        if confirm not in ['yes', 'y', 'نعم']:
            print("❌ تم إلغاء العملية")
            conn.close()
            return False
        
        # حذف الطالب
        cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        conn.commit()
        
        print(f"\n✅ تم حذف الطالب {student_id} بنجاح!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def delete_student_by_email(email):
    """حذف طالب بالبريد الإلكتروني"""
    if not os.path.exists(DB_PATH):
        print(f"❌ قاعدة البيانات غير موجودة: {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # التحقق من وجود الطالب
        cursor.execute("SELECT * FROM students WHERE email = ?", (email,))
        student = cursor.fetchone()
        
        if not student:
            print(f"❌ لا يوجد طالب بالبريد {email}")
            conn.close()
            return False
        
        print(f"\n📋 بيانات الطالب:")
        print(f"   ID: {student[0]}")
        print(f"   رقم الطالب: {student[1]}")
        print(f"   الاسم: {student[2]}")
        print(f"   البريد: {student[3]}")
        
        # تأكيد الحذف
        confirm = input(f"\n⚠️ هل أنت متأكد من حذف الطالب؟ (yes/no): ").strip().lower()
        
        if confirm not in ['yes', 'y', 'نعم']:
            print("❌ تم إلغاء العملية")
            conn.close()
            return False
        
        # حذف الطالب
        cursor.execute("DELETE FROM students WHERE email = ?", (email,))
        conn.commit()
        
        print(f"\n✅ تم حذف الطالب بنجاح!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False

def list_all_students():
    """عرض جميع الطلاب"""
    if not os.path.exists(DB_PATH):
        print(f"❌ قاعدة البيانات غير موجودة: {DB_PATH}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM students ORDER BY student_id")
        students = cursor.fetchall()
        
        if not students:
            print("\n❌ لا يوجد طلاب في قاعدة البيانات")
            conn.close()
            return
        
        print(f"\n📋 قائمة الطلاب ({len(students)} طالب):")
        print("="*80)
        
        for student in students:
            print(f"\n   رقم الطالب: {student[1]}")
            print(f"   الاسم: {student[2]}")
            print(f"   البريد: {student[3]}")
            print("-"*80)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ خطأ: {e}")

def main():
    """القائمة الرئيسية"""
    print("="*80)
    print("  🗑️ أداة حذف الطلاب / Delete Student Tool")
    print("="*80)
    
    while True:
        print("\nاختر العملية:")
        print("  1️⃣  - حذف طالب برقم الطالب")
        print("  2️⃣  - حذف طالب بالبريد الإلكتروني")
        print("  3️⃣  - عرض جميع الطلاب")
        print("  0️⃣  - خروج")
        print("-"*80)
        
        choice = input("\nأدخل اختيارك: ").strip()
        
        if choice == "1":
            student_id = input("\nأدخل رقم الطالب: ").strip()
            if student_id:
                delete_student_by_id(student_id)
        
        elif choice == "2":
            email = input("\nأدخل البريد الإلكتروني: ").strip()
            if email:
                delete_student_by_email(email)
        
        elif choice == "3":
            list_all_students()
        
        elif choice == "0":
            print("\n👋 إلى اللقاء!")
            break
        
        else:
            print("\n❌ اختيار غير صحيح!")
        
        input("\n📌 اضغط Enter للمتابعة...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 تم الإيقاف بواسطة المستخدم")
    except Exception as e:
        print(f"\n❌ خطأ: {e}")