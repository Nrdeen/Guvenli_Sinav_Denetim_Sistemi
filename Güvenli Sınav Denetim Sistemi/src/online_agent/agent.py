"""
Online Agent - Student Webcam Monitoring
Each student runs this on their computer to be monitored remotely
"""

import cv2
import logging
import requests
import time
from datetime import datetime
from src.detection.face_id import recognize_student, draw_face_boxes, get_primary_student
from src.detection.eye_tracking import EyeTracker
from src.detection.mouth_detection import MouthDetector
from src.detection.object_detection import ObjectDetector
from src.utils.violation_logger import ViolationLogger
from src.utils.student_loader import list_all_students

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OnlineStudentMonitor:
    """Monitor individual student via webcam"""
    
    def __init__(self, student_id=None, student_name=None, exam_code=None):
        self.student_id = student_id
        self.student_name = student_name
        self.exam_code = exam_code
        self.violation_logger = ViolationLogger()
        
        # Initialize detectors
        self.eye_tracker = EyeTracker()
        self.mouth_detector = MouthDetector()
        self.object_detector = ObjectDetector()
        
        self.running = False
        self.frame_count = 0
        
        # Violation thresholds
        self.looking_away_frames = 0
        self.looking_away_threshold = 30  # ~1 second at 30fps
        self.no_face_frames = 0
        self.no_face_threshold = 60  # ~2 seconds
    
    def wait_for_exam_start(self):
        """انتظار بدء الاختبار من قبل المعلم"""
        if not self.exam_code:
            print("⚠️ لم يتم تحديد رمز الاختبار، بدء المراقبة فوراً")
            return True
            
        # التحقق من تسجيل الطالب في الاختبار أولاً
        try:
            response = requests.get(f"http://localhost:8001/api/exams/{self.exam_code}/verify-student/{self.student_id}", timeout=5)
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
            
        print("="*60)
        print("⏳ انتظار بدء الاختبار...")
        print(f"📝 رمز الاختبار: {self.exam_code}")
        print(f"👤 الطالب: {self.student_name} ({self.student_id})")
        print("="*60)
        print("الكاميرا لن تفتح إلا عندما يبدأ المعلم الاختبار")
        print("اضغط Ctrl+C للخروج من الانتظار\n")
        
        while not self.running:
            try:
                # التحقق من حالة الاختبار
                response = requests.get("http://localhost:8001/api/exams/{}/info".format(self.exam_code), timeout=5)
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
            time.sleep(5)
        
        return False
    
    def start_monitoring(self):
        """Start monitoring the student"""
        logger.info(f"💻 Starting online monitoring for: {self.student_name} ({self.student_id})")
        
        # انتظار بدء الاختبار
        if not self.wait_for_exam_start():
            return
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            logger.error("❌ Cannot open webcam!")
            print("\n❌ Error: Cannot access webcam!")
            print("Please check your camera permissions and try again.")
            input("\nPress Enter to return to menu...")
            return
        
        self.running = True
        
        print(f"\n✅ Monitoring started for: {self.student_name}")
        print("📹 Your webcam is now active")
        print("⚠️  Do not close this window during the exam")
        print("Press 'q' to stop monitoring\n")
        
        while self.running:
            ret, frame = cap.read()
            
            if not ret:
                logger.warning("Failed to read frame from webcam")
                break
            
            self.frame_count += 1
            
            # Face recognition
            recognized = recognize_student(frame)
            
            if recognized:
                detected_id, detected_name, loc, conf = recognized[0]
                
                # Check if the right student
                if self.student_id and detected_id != self.student_id and detected_id != "unknown":
                    self._log_violation(
                        "wrong_student",
                        f"Different student detected: {detected_name}",
                        frame
                    )
                
                # Reset no-face counter
                self.no_face_frames = 0
                
                # Eye tracking
                if self.frame_count % 5 == 0:  # Check every 5 frames
                    gaze_direction = self.eye_tracker.detect_gaze(frame)
                    
                    if gaze_direction and gaze_direction != "center":
                        self.looking_away_frames += 1
                        
                        if self.looking_away_frames > self.looking_away_threshold:
                            self._log_violation(
                                "looking_away",
                                f"Student looking {gaze_direction}",
                                frame
                            )
                            self.looking_away_frames = 0  # Reset after logging
                    else:
                        self.looking_away_frames = 0
                
                # Mouth detection (talking)
                if self.frame_count % 10 == 0:  # Check every 10 frames
                    is_talking = self.mouth_detector.detect_speaking(frame)
                    
                    if is_talking:
                        self._log_violation(
                            "talking",
                            "Student appears to be talking",
                            frame
                        )
            else:
                # No face detected
                self.no_face_frames += 1
                
                if self.no_face_frames > self.no_face_threshold:
                    self._log_violation(
                        "no_face",
                        "Student left the camera view",
                        frame
                    )
                    self.no_face_frames = 0  # Reset after logging
            
            # Object detection
            if self.frame_count % 15 == 0:  # Check every 15 frames
                detected_objects = self.object_detector.detect(frame)
                
                for obj in detected_objects:
                    obj_class = obj.get("class", "")
                    if obj_class in ["cell phone", "book", "laptop"]:
                        self._log_violation(
                            "prohibited_object",
                            f"Prohibited object detected: {obj_class}",
                            frame
                        )
                
                # Draw objects
                frame = self._draw_objects(frame, detected_objects)
            
            # Draw student name boxes (like classroom monitoring)
            frame = self._draw_student_boxes(frame, recognized)
            
            # Add overlay
            self._add_overlay(frame, recognized)
            
            # Display
            cv2.imshow(f"Online Monitoring - {self.student_name}", frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        self.running = False
        
        logger.info(f"✅ Monitoring stopped for {self.student_name}")
        print(f"\n✅ Monitoring session ended for {self.student_name}")
        input("Press Enter to return to menu...")
    
    def _log_violation(self, violation_type, description, frame):
        """Log a violation"""
        self.violation_logger.log_violation(
            violation_type=violation_type,
            student_id=self.student_id or "unknown",
            student_name=self.student_name or "Unknown",
            description=description,
            frame=frame,
            camera_id="online_webcam"
        )
        
        logger.warning(f"⚠️  Violation: {description}")
    
    def _draw_student_boxes(self, frame, recognized_students):
        """
        Draw bounding boxes with student names (matching classroom monitoring style)
        """
        if not recognized_students:
            return frame
        
        for sid, name, (top, right, bottom, left), confidence in recognized_students:
            # Set color based on recognition
            if sid == "unknown":
                color = (0, 0, 255)  # Red for unknown
                label = "Unknown"
            else:
                color = (0, 255, 0)  # Green for known students
                label = name  # Display student name
            
            # Draw bounding box
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Draw label text above the box
            cv2.putText(
                frame,
                label,
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )
        
        return frame
    
    def _draw_objects(self, frame, objects):
        """Draw detected objects"""
        for obj in objects:
            x1, y1, x2, y2 = obj.get("bbox", [0, 0, 0, 0])
            label = obj.get("class", "")
            confidence = obj.get("confidence", 0.0)
            
            color = (0, 0, 255) if label in ["cell phone", "book", "laptop"] else (255, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            label_text = f"{label} {int(confidence*100)}%"
            cv2.putText(frame, label_text, (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame
    
    def _add_overlay(self, frame, students):
        """Add monitoring overlay"""
        h, w = frame.shape[:2]
        
        # Top overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 50), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)
        
        # Student info
        cv2.putText(frame, f"Student: {self.student_name}", (10, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # ID
        cv2.putText(frame, f"ID: {self.student_id}", (10, 45),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, timestamp, (w - 100, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Status
        status_color = (0, 255, 0) if students else (0, 0, 255)
        status_text = "Face Detected" if students else "No Face"
        cv2.putText(frame, status_text, (w - 200, 45),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1)


def select_student():
    """Let user select which student they are"""
    students = list_all_students()
    
    if not students:
        print("\n❌ No students registered!")
        print("Please add students to config/students.yaml first.")
        return None, None
    
    print("\n📋 Select Your Student Profile:")
    print("-" * 60)
    
    for i, student in enumerate(students, 1):
        print(f"{i}. {student.get('name', 'N/A')} (ID: {student.get('id', 'N/A')})")
    
    print("-" * 60)
    
    while True:
        try:
            choice = input("\nEnter student number (or 0 to cancel): ").strip()
            
            if choice == "0":
                return None, None
            
            idx = int(choice) - 1
            
            if 0 <= idx < len(students):
                selected = students[idx]
                return selected.get("id"), selected.get("name")
            else:
                print("❌ Invalid selection. Try again.")
        
        except ValueError:
            print("❌ Please enter a valid number.")
        except KeyboardInterrupt:
            return None, None


def start_online_monitoring():
    """Start online monitoring mode"""
    print("\n💻 Online Monitoring - Student Webcam")
    print("=" * 60)
    
    # Student selection
    student_id, student_name = select_student()
    
    if not student_id:
        print("\n❌ No student selected. Returning to menu...")
        input("Press Enter to continue...")
        return
    
    # Exam code input
    print("\n📝 Enter Exam Code:")
    exam_code = input("Exam Code: ").strip().upper()
    
    if not exam_code:
        print("\n❌ Exam code is required!")
        input("Press Enter to continue...")
        return
    
    # Start monitoring
    monitor = OnlineStudentMonitor(student_id, student_name, exam_code)
    monitor.start_monitoring()


if __name__ == "__main__":
    start_online_monitoring()
