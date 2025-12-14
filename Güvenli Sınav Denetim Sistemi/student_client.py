"""
Student Monitoring Client - يرسل البيانات للخادم المركزي
"""
import cv2
import requests
import time
import json
from datetime import datetime
import threading
import sys
import os

# إعدادات الاتصال بالخادم
API_URL = "http://localhost:8001"  # تغييره إلى عنوان الخادم الفعلي
HEARTBEAT_INTERVAL = 5  # ثواني

class StudentMonitoringClient:
    def __init__(self, student_id: str, exam_code: str, camera_index: int = 0):
        self.student_id = student_id
        self.exam_code = exam_code
        self.camera_index = camera_index
        self.is_running = False
        self.heartbeat_thread = None
        
        # التحقق من الاتصال بالخادم
        try:
            response = requests.get(f"{API_URL}/")
            print("✅ تم الاتصال بالخادم بنجاح")
        except:
            print("❌ فشل الاتصال بالخادم!")
            print(f"تأكد من تشغيل الخادم على: {API_URL}")
            sys.exit(1)
    
    def start_heartbeat(self):
        """بدء إرسال نبضات القلب للخادم"""
        def heartbeat_loop():
            while self.is_running:
                try:
                    response = requests.post(
                        f"{API_URL}/api/heartbeat",
                        json={
                            "student_id": self.student_id,
                            "exam_code": self.exam_code,
                            "is_active": True
                        },
                        timeout=5
                    )
                    if response.status_code == 200:
                        print(f"💓 تم إرسال نبضة القلب - {datetime.now().strftime('%H:%M:%S')}")
                    else:
                        print(f"⚠️ خطأ في نبضة القلب: {response.status_code}")
                except Exception as e:
                    print(f"❌ فشل إرسال نبضة القلب: {e}")
                
                time.sleep(HEARTBEAT_INTERVAL)
        
        self.heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
    
    def send_violation(self, violation_type: str, description: str, severity: str = "medium", confidence: float = 0.0):
        """إرسال انتهاك للخادم"""
        try:
            response = requests.post(
                f"{API_URL}/api/violations",
                json={
                    "student_id": self.student_id,
                    "exam_code": self.exam_code,
                    "violation_type": violation_type,
                    "severity": severity,
                    "description": description,
                    "confidence_score": confidence
                },
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"🚨 تم تسجيل انتهاك: {violation_type}")
                return True
            else:
                print(f"⚠️ خطأ في تسجيل الانتهاك: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ فشل إرسال الانتهاك: {e}")
            return False
    
    def wait_for_exam_start(self):
        """انتظار بدء الاختبار من قبل المعلم"""
        print("="*60)
        print("⏳ انتظار بدء الاختبار...")
        print(f"📝 رمز الاختبار: {self.exam_code}")
        print(f"👤 رقم الطالب: {self.student_id}")
        print("="*60)
        
        # التحقق من تسجيل الطالب في الاختبار أولاً
        try:
            response = requests.get(f"{API_URL}/api/exams/{self.exam_code}/verify-student/{self.student_id}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if not data.get("registered", False):
                    print(f"❌ خطأ: {data.get('message', 'الطالب غير مسجل في الاختبار')}")
                    return False
                else:
                    print(f"✅ تم التحقق من تسجيل الطالب: {data.get('student_name')}")
                    print(f"📚 اسم الاختبار: {data.get('exam_name')}")
            else:
                print(f"❌ فشل في التحقق من تسجيل الطالب: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ خطأ في الاتصال بالخادم: {e}")
            return False
        
        print("الكاميرا لن تفتح إلا عندما يبدأ المعلم الاختبار")
        print("اضغط 'q' للخروج من الانتظار\n")
        
        while True:
            try:
                # التحقق من حالة الاختبار
                response = requests.get(f"{API_URL}/api/exams/{self.exam_code}/info", timeout=5)
                if response.status_code == 200:
                    exam_data = response.json()
                    if exam_data.get("status") == "active":
                        print("🎯 تم بدء الاختبار! بدء المراقبة الآن...")
                        return True
                    else:
                        print(f"📋 حالة الاختبار: {exam_data.get('status', 'غير محدد')}")
                else:
                    print(f"⚠️ فشل التحقق من حالة الاختبار: {response.status_code}")
            except Exception as e:
                print(f"❌ خطأ في الاتصال بالخادم: {e}")
            
            # انتظار 5 ثواني قبل التحقق مرة أخرى
            import time
            time.sleep(5)
            
            # التحقق من الخروج
            try:
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b'q':
                        print("\n🛑 إلغاء الانتظار...")
                        return False
            except:
                pass  # في حالة عدم توفر msvcrt
    
    def start_monitoring(self):
        """بدء المراقبة بعد انتظار إشارة البدء"""
        self.is_running = True
        self.start_heartbeat()
        
        # انتظار بدء الاختبار
        if not self.wait_for_exam_start():
            self.is_running = False
            return
        
        print("="*60)
        print(f"📹 بدء مراقبة الطالب: {self.student_id}")
        print(f"📝 رمز الاختبار: {self.exam_code}")
        print(f"🌐 الخادم: {API_URL}")
        print("="*60)
        
        # فتح الكاميرا المحددة
        cap = cv2.VideoCapture(self.camera_index)
        
        if not cap.isOpened():
            print("❌ فشل فتح الكاميرا!")
            self.is_running = False
            return
        
        print("\n✅ تم فتح الكاميرا بنجاح")
        print("\nاضغط 'q' للخروج")
        print("اضغط 'v' لإرسال انتهاك تجريبي\n")
        
        violation_count = 0
        frame_count = 0
        
        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                print("❌ فشل قراءة الإطار من الكاميرا")
                break
            
            frame_count += 1
            
            # عرض الإطار
            cv2.putText(frame, f"Student: {self.student_id}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Exam: {self.exam_code}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Violations: {violation_count}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, "Press 'q' to quit, 'v' for test violation", (10, frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow('Student Monitoring - اضغط q للخروج', frame)
            
            # التحكم بالمفاتيح
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\n🛑 إيقاف المراقبة...")
                break
            elif key == ord('v'):
                # إرسال انتهاك تجريبي
                if self.send_violation(
                    violation_type="looking_away",
                    description="اختبار انتهاك - النظر بعيداً عن الشاشة",
                    severity="medium",
                    confidence=0.85
                ):
                    violation_count += 1
        
        # التنظيف
        cap.release()
        cv2.destroyAllWindows()
        self.is_running = False
        
        # إرسال نبضة قلب أخيرة لإيقاف الجلسة
        try:
            requests.post(
                f"{API_URL}/api/heartbeat",
                json={
                    "student_id": self.student_id,
                    "exam_code": self.exam_code,
                    "is_active": False
                },
                timeout=5
            )
        except:
            pass
        
        print("\n✅ تم إيقاف المراقبة بنجاح")
        print(f"📊 إجمالي الانتهاكات المسجلة: {violation_count}")

def detect_cameras():
    """اكتشاف الكاميرات المتاحة"""
    print("\n🔍 جاري البحث عن الكاميرات المتاحة...")
    available_cameras = []
    
    for i in range(10):  # فحص حتى 10 كاميرات
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            backend = cap.getBackendName()
            
            available_cameras.append({
                "index": i,
                "resolution": f"{width}x{height}",
                "backend": backend
            })
            
            print(f"   ✅ الكاميرا {i}: {width}x{height} ({backend})")
            cap.release()
    
    return available_cameras

def main():
    """البرنامج الرئيسي"""
    print("="*60)
    print("        Güvenli Sınav - برنامج مراقبة الطالب")
    print("="*60)
    
    # اكتشاف الكاميرات المتاحة
    cameras = detect_cameras()
    
    if not cameras:
        print("\n❌ لم يتم العثور على أي كاميرات!")
        print("💡 تأكد من توصيل الكاميرا وتثبيت التعريفات")
        return
    
    # اختيار الكاميرا
    camera_index = 0
    if len(cameras) > 1:
        print(f"\n📹 تم العثور على {len(cameras)} كاميرا/كاميرات")
        print("اختر الكاميرا المطلوبة:")
        for cam in cameras:
            print(f"   [{cam['index']}] الكاميرا {cam['index']} - {cam['resolution']}")
        
        try:
            choice = input(f"\nأدخل رقم الكاميرا (0-{len(cameras)-1}) [الافتراضي: 0]: ").strip()
            if choice:
                camera_index = int(choice)
                if camera_index < 0 or camera_index >= len(cameras):
                    print("⚠️ رقم غير صحيح، سيتم استخدام الكاميرا 0")
                    camera_index = 0
        except ValueError:
            print("⚠️ إدخال غير صحيح، سيتم استخدام الكاميرا 0")
            camera_index = 0
    
    print(f"\n✅ تم اختيار الكاميرا {camera_index}")
    
    # طلب بيانات الطالب
    student_id = input("\n🎓 أدخل رقم الطالب (مثال: STU001): ").strip()
    exam_code = input("📝 أدخل رمز الاختبار (مثال: PROG2025): ").strip()
    
    if not student_id or not exam_code:
        print("❌ يجب إدخال رقم الطالب ورمز الاختبار!")
        return
    
    # إنشاء العميل وبدء المراقبة
    client = StudentMonitoringClient(student_id, exam_code, camera_index)
    
    try:
        client.start_monitoring()
    except KeyboardInterrupt:
        print("\n\n🛑 تم إيقاف البرنامج بواسطة المستخدم")
        client.is_running = False

if __name__ == "__main__":
    main()
