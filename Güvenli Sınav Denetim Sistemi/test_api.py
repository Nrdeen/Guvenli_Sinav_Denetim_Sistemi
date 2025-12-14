import requests
import json

API_URL = "http://localhost:8001"

print("=" * 60)
print("اختبار API - جميع الطلاب")
print("=" * 60)

try:
    response = requests.get(f"{API_URL}/api/students/all", timeout=5)
    
    if response.status_code == 200:
        students = response.json()
        print(f"\n✅ تم جلب {len(students)} طالب/طالبة\n")
        
        for i, student in enumerate(students, 1):
            print(f"{i}. ID: {student['id']}")
            print(f"   Name: {student['name']}")
            print(f"   Email: {student['email']}")
            print(f"   Exam Code: {student['exam_code']}")
            print("-" * 40)
    else:
        print(f"❌ خطأ: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ خطأ في الاتصال: {e}")

print("\n" + "=" * 60)
print("اختبار API - طلاب اختبار MATH2025")
print("=" * 60)

try:
    response = requests.get(f"{API_URL}/api/exams/MATH2025/registered-students", timeout=5)
    
    if response.status_code == 200:
        students = response.json()
        print(f"\n✅ تم جلب {len(students)} طالب/طالبة مسجلين في MATH2025\n")
        
        for i, student in enumerate(students, 1):
            print(f"{i}. ID: {student['id']}")
            print(f"   Name: {student['name']}")
            print(f"   Email: {student['email']}")
            print("-" * 40)
    else:
        print(f"❌ خطأ: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ خطأ في الاتصال: {e}")