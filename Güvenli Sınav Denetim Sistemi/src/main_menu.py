"""
Main Menu - Exam Proctoring System
Provides 3 monitoring modes: Classroom, Online, or Both
"""

import sys
import os


def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Print system banner"""
    print("=" * 60)
    print("         EXAM PROCTORING SYSTEM - نظام مراقبة الامتحانات")
    print("=" * 60)
    print()


def show_menu():
    """Display main menu and handle user selection"""
    
    while True:
        clear_screen()
        print_banner()
        
        print("Select Monitoring Mode / اختر وضع المراقبة:")
        print()
        print("  1) 🏫 Classroom Monitoring - مراقبة الصف")
        print("     (Multiple RTSP cameras for physical classroom)")
        print()
        print("  2) 💻 Online Monitoring - مراقبة أونلاين")
        print("     (Individual student webcams for remote exam)")
        print()
        print("  3) 🔄 Combined Monitoring - مراقبة مشتركة")
        print("     (Both classroom + online students)")
        print()
        print("  4) ⚙️  Settings - الإعدادات")
        print()
        print("  5) ▶️  Start Exam - بدء اختبار")
        print("     (Start a scheduled exam for monitoring)")
        print()
        print("  0) ❌ Exit - خروج")
        print()
        print("=" * 60)
        
        choice = input("\nEnter your choice / أدخل اختيارك: ").strip()
        
        if choice == "1":
            start_classroom_mode()
        elif choice == "2":
            start_online_mode()
        elif choice == "3":
            start_combined_mode()
        elif choice == "4":
            show_settings()
        elif choice == "5":
            start_exam_mode()
        elif choice == "0":
            print("\n👋 Goodbye! - مع السلامة")
            sys.exit(0)
        else:
            print("\n❌ Invalid choice! Please select 0, 1, 2, 3, 4, or 5")
            input("Press Enter to continue...")


def start_classroom_mode():
    """Start classroom monitoring mode"""
    try:
        print("\n🏫 Starting Classroom Monitoring Mode...")
        print("Loading cameras from config/cameras.yaml...")
        
        from src.classroom_monitor.rtsp_reader import start_classroom_monitoring
        start_classroom_monitoring()
        
    except ImportError as e:
        print(f"\n❌ Error importing classroom module: {e}")
        print("Make sure all required files are present.")
        input("\nPress Enter to return to menu...")
    except Exception as e:
        print(f"\n❌ Error starting classroom mode: {e}")
        input("\nPress Enter to return to menu...")


def start_online_mode():
    """Start online monitoring mode"""
    try:
        print("\n💻 Starting Online Monitoring Mode...")
        print("Initializing student webcam monitoring...")
        
        from src.online_agent.agent import start_online_monitoring
        start_online_monitoring()
        
    except ImportError as e:
        print(f"\n❌ Error importing online module: {e}")
        print("Make sure all required files are present.")
        input("\nPress Enter to return to menu...")
    except Exception as e:
        print(f"\n❌ Error starting online mode: {e}")
        input("\nPress Enter to return to menu...")


def start_combined_mode():
    """Start combined monitoring mode (both classroom + online)"""
    try:
        print("\n🔄 Starting Combined Monitoring Mode...")
        print("Launching both classroom and online monitoring...")
        
        from src.combined.run_both import start_combined_monitoring
        start_combined_monitoring()
        
    except ImportError as e:
        print(f"\n❌ Error importing combined module: {e}")
        print("Make sure all required files are present.")
        input("\nPress Enter to return to menu...")
    except Exception as e:
        print(f"\n❌ Error starting combined mode: {e}")
        input("\nPress Enter to return to menu...")


def show_settings():
    """Show settings and configuration options"""
    clear_screen()
    print_banner()
    print("⚙️  SETTINGS - الإعدادات\n")
    
    print("1) View Students List - عرض قائمة الطلاب")
    print("2) View Camera Configuration - عرض إعدادات الكاميرات")
    print("3) Test Face Recognition - اختبار التعرف على الوجه")
    print("4) View System Information - معلومات النظام")
    print("0) Back to Main Menu - العودة للقائمة الرئيسية")
    print()
    
    choice = input("Enter your choice: ").strip()
    
    if choice == "1":
        view_students()
    elif choice == "2":
        view_cameras()
    elif choice == "3":
        test_face_recognition()
    elif choice == "4":
        view_system_info()
    elif choice == "0":
        return
    else:
        print("Invalid choice!")
        input("Press Enter to continue...")


def view_students():
    """Display registered students"""
    try:
        from src.utils.student_loader import list_all_students
        
        students = list_all_students()
        
        print("\n📋 Registered Students:")
        print("-" * 60)
        
        if not students:
            print("No students registered yet!")
            print("Add students in config/students.yaml")
        else:
            for i, student in enumerate(students, 1):
                print(f"{i}. {student.get('name', 'N/A')} (ID: {student.get('id', 'N/A')})")
                print(f"   Photo: {student.get('photo', 'N/A')}")
                
                # Check if photo exists
                photo_path = student.get('photo', '')
                if photo_path and os.path.exists(photo_path):
                    print("   Status: ✅ Photo found")
                else:
                    print("   Status: ❌ Photo not found")
                print()
        
        print("-" * 60)
        
    except Exception as e:
        print(f"Error loading students: {e}")
    
    input("\nPress Enter to continue...")


def view_cameras():
    """Display camera configuration"""
    try:
        import yaml
        
        with open("config/cameras.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        cameras = config.get("cameras", [])
        
        print("\n📹 Camera Configuration:")
        print("-" * 60)
        
        if not cameras:
            print("No cameras configured!")
            print("Add cameras in config/cameras.yaml")
        else:
            for i, cam in enumerate(cameras, 1):
                print(f"{i}. {cam.get('name', 'N/A')} (ID: {cam.get('id', 'N/A')})")
                print(f"   RTSP: {cam.get('rtsp', 'N/A')}")
                print()
        
        print("-" * 60)
        
    except Exception as e:
        print(f"Error loading cameras: {e}")
    
    input("\nPress Enter to continue...")


def test_face_recognition():
    """Test face recognition with webcam"""
    try:
        print("\n🎥 Testing Face Recognition...")
        print("Press 'q' to quit")
        
        from src.detection.face_id import recognize_student, draw_face_boxes
        import cv2
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Cannot open webcam!")
            input("Press Enter to continue...")
            return
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Recognize faces
            results = recognize_student(frame)
            
            # Draw boxes
            frame = draw_face_boxes(frame, results)
            
            # Display
            cv2.imshow("Face Recognition Test - Press 'q' to quit", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"Error testing face recognition: {e}")
        input("Press Enter to continue...")


def view_system_info():
    """Display system information"""
    import platform
    
    print("\n💻 System Information:")
    print("-" * 60)
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")
    print("-" * 60)
    
    input("\nPress Enter to continue...")


def start_exam_mode():
    """Start an exam for monitoring"""
    try:
        print("\n▶️ Start Exam Mode")
        print("=" * 60)
        
        exam_code = input("Enter Exam Code / أدخل رمز الاختبار: ").strip().upper()
        
        if not exam_code:
            print("\n❌ Exam code is required!")
            input("Press Enter to continue...")
            return
        
        # Import and run the start exam script
        import subprocess
        import os
        
        script_path = os.path.join(os.getcwd(), "start_exam.py")
        
        if os.path.exists(script_path):
            result = subprocess.run([sys.executable, script_path, exam_code], 
                                  capture_output=True, text=True)
            
            print(result.stdout)
            if result.stderr:
                print(f"Errors: {result.stderr}")
        else:
            print(f"\n❌ start_exam.py not found at: {script_path}")
        
        input("\nPress Enter to continue...")
        
    except Exception as e:
        print(f"\n❌ Error starting exam: {e}")
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        show_menu()
    except KeyboardInterrupt:
        print("\n\n👋 System interrupted. Goodbye!")
        sys.exit(0)
