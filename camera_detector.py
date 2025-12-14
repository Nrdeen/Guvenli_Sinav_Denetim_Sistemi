"""
أداة للكشف عن الكاميرات المتاحة في النظام
Camera Detection Utility
"""
import cv2
import sys

def detect_available_cameras(max_cameras=10):
    """
    اكتشاف جميع الكاميرات المتاحة
    Detect all available cameras
    
    Args:
        max_cameras: الحد الأقصى لعدد الكاميرات للفحص
    
    Returns:
        قائمة بالكاميرات المتاحة
    """
    available_cameras = []
    
    print("🔍 جاري البحث عن الكاميرات المتاحة...")
    print("🔍 Searching for available cameras...")
    print("="*60)
    
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # الحصول على معلومات الكاميرا
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = cap.get(cv2.CAP_PROP_FPS)
            backend = cap.getBackendName()
            
            camera_info = {
                "index": i,
                "name": f"Camera {i}",
                "resolution": f"{int(width)}x{int(height)}",
                "fps": int(fps) if fps > 0 else "Unknown",
                "backend": backend
            }
            
            available_cameras.append(camera_info)
            
            # طباعة المعلومات
            print(f"✅ تم العثور على كاميرا {i}")
            print(f"   📹 الدقة: {camera_info['resolution']}")
            print(f"   🎬 FPS: {camera_info['fps']}")
            print(f"   🔧 Backend: {camera_info['backend']}")
            print("-"*60)
            
            cap.release()
    
    return available_cameras

def test_camera(camera_index):
    """
    اختبار كاميرا معينة
    Test a specific camera
    
    Args:
        camera_index: رقم الكاميرا للاختبار
    """
    print(f"\n🎥 اختبار الكاميرا {camera_index}...")
    print(f"🎥 Testing camera {camera_index}...")
    
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print(f"❌ فشل فتح الكاميرا {camera_index}")
        print(f"❌ Failed to open camera {camera_index}")
        return False
    
    print(f"✅ تم فتح الكاميرا {camera_index} بنجاح")
    print("📸 اضغط 'q' للخروج من معاينة الكاميرا")
    print("📸 Press 'q' to exit camera preview")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("❌ فشل قراءة الإطار من الكاميرا")
            break
        
        # عرض الإطار
        cv2.imshow(f'Camera {camera_index} Preview', frame)
        
        # الخروج عند الضغط على 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"✅ تم إغلاق معاينة الكاميرا {camera_index}")
    return True

def main():
    """الدالة الرئيسية"""
    print("="*60)
    print("🎥 أداة الكشف عن الكاميرات")
    print("🎥 Camera Detection Tool")
    print("="*60)
    
    # اكتشاف الكاميرات
    cameras = detect_available_cameras()
    
    if not cameras:
        print("\n❌ لم يتم العثور على أي كاميرات!")
        print("❌ No cameras found!")
        print("\n💡 تأكد من:")
        print("   1. توصيل الكاميرا بشكل صحيح")
        print("   2. تثبيت تعريفات الكاميرا")
        print("   3. منح الصلاحيات للتطبيق للوصول للكاميرا")
        return
    
    print(f"\n✅ تم العثور على {len(cameras)} كاميرا/كاميرات")
    print(f"✅ Found {len(cameras)} camera(s)")
    
    # عرض قائمة الكاميرات
    print("\n📋 الكاميرات المتاحة:")
    print("📋 Available cameras:")
    for cam in cameras:
        print(f"\n   [{cam['index']}] {cam['name']}")
        print(f"       📹 الدقة: {cam['resolution']}")
        print(f"       🎬 FPS: {cam['fps']}")
        print(f"       🔧 Backend: {cam['backend']}")
    
    # اختبار الكاميرات
    print("\n" + "="*60)
    print("🧪 اختبار الكاميرات")
    print("🧪 Camera Testing")
    print("="*60)
    
    while True:
        try:
            choice = input(f"\nأدخل رقم الكاميرا للاختبار (0-{len(cameras)-1}) أو 'q' للخروج: ")
            
            if choice.lower() == 'q':
                print("👋 إلى اللقاء!")
                break
            
            camera_index = int(choice)
            
            if 0 <= camera_index < len(cameras):
                test_camera(camera_index)
            else:
                print(f"❌ رقم غير صحيح! اختر من 0 إلى {len(cameras)-1}")
        
        except ValueError:
            print("❌ يرجى إدخال رقم صحيح!")
        except KeyboardInterrupt:
            print("\n\n👋 تم الإيقاف بواسطة المستخدم")
            break

if __name__ == "__main__":
    main()