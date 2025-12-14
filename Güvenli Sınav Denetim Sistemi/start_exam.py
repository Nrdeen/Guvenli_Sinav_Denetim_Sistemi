"""
Script to start an exam via API
"""
import requests
import sys

API_URL = "http://localhost:8001"

def start_exam(exam_code):
    """Start an exam by code"""
    try:
        response = requests.post(f"{API_URL}/api/exams/{exam_code}/start")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ تم بدء الاختبار بنجاح!")
            print(f"رمز الاختبار: {exam_code}")
            print(f"الحالة: {data.get('status')}")
        else:
            print(f"❌ فشل في بدء الاختبار: {response.status_code}")
            print(f"الرد: {response.text}")
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python start_exam.py <exam_code>")
        print("Example: python start_exam.py MATH101")
        sys.exit(1)
    
    exam_code = sys.argv[1].upper()
    start_exam(exam_code)