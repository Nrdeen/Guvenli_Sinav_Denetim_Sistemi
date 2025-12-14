"""
Classroom Monitor - RTSP Camera Reader
Monitors multiple classroom cameras with face recognition and cheating detection
"""

import cv2
import yaml
import os
import logging
import threading
from datetime import datetime
from src.detection.face_id import recognize_student, draw_face_boxes
from src.detection.multi_face import MultiPersonDetector
from src.detection.object_detection import ObjectDetector
from src.utils.violation_logger import ViolationLogger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClassroomCamera:
    """Handle individual classroom camera"""
    
    def __init__(self, camera_config, violation_logger):
        self.camera_id = camera_config.get("id", "unknown")
        self.camera_name = camera_config.get("name", "Camera")
        self.rtsp_url = camera_config.get("rtsp", "")
        self.violation_logger = violation_logger
        self.running = False
        
        # Initialize detectors
        self.multi_face_detector = MultiPersonDetector()
        self.object_detector = ObjectDetector()
        
    def start(self):
        """Start monitoring this camera"""
        self.running = True
        thread = threading.Thread(target=self._monitor_loop, daemon=True)
        thread.start()
        return thread
    
    def stop(self):
        """Stop monitoring"""
        self.running = False
    
    def _monitor_loop(self):
        """Main monitoring loop for this camera"""
        logger.info(f"🎥 Starting camera: {self.camera_name} ({self.camera_id})")
        
        # Try to open camera
        # If RTSP URL is numeric, treat as webcam index
        try:
            source = int(self.rtsp_url)
        except ValueError:
            source = self.rtsp_url
        
        cap = cv2.VideoCapture(source)
        
        if not cap.isOpened():
            logger.error(f"❌ Cannot open camera: {self.camera_name} - {self.rtsp_url}")
            return
        
        logger.info(f"✅ Camera {self.camera_name} is running")
        
        frame_count = 0
        
        while self.running:
            ret, frame = cap.read()
            
            if not ret:
                logger.warning(f"⚠️  Failed to read frame from {self.camera_name}")
                break
            
            frame_count += 1
            
            # Process every 5th frame for performance
            if frame_count % 5 == 0:
                # Face recognition
                recognized_students = recognize_student(frame)
                
                # Draw student names with boxes (like the example code)
                frame = self._draw_student_boxes(frame, recognized_students)
                
                # Check for multiple people (potential cheating)
                if len(recognized_students) > 1:
                    self._log_violation(
                        "multiple_faces",
                        f"Multiple people detected in {self.camera_name}",
                        frame,
                        recognized_students
                    )
                
                # Object detection (detect phones, books, etc.)
                detected_objects = self.object_detector.detect(frame)
                
                for obj in detected_objects:
                    obj_class = obj.get("class", "")
                    if obj_class in ["cell phone", "book", "laptop"]:
                        self._log_violation(
                            "prohibited_object",
                            f"{obj_class} detected in {self.camera_name}",
                            frame,
                            recognized_students
                        )
                
                # Draw object detections
                frame = self._draw_objects(frame, detected_objects)
            
            # Add camera info overlay
            self._add_camera_overlay(frame, recognized_students if frame_count % 5 == 0 else [])
            
            # Display frame
            cv2.imshow(f"{self.camera_name} - {self.camera_id}", frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        cap.release()
        cv2.destroyWindow(f"{self.camera_name} - {self.camera_id}")
        logger.info(f"🛑 Camera {self.camera_name} stopped")
    
    def _log_violation(self, violation_type, description, frame, students):
        """Log a violation"""
        student_info = []
        for sid, name, loc, conf in students:
            if sid != "unknown":
                student_info.append({"id": sid, "name": name})
        
        self.violation_logger.log_violation(
            violation_type=violation_type,
            student_id=student_info[0]["id"] if student_info else "unknown",
            student_name=student_info[0]["name"] if student_info else "Unknown",
            description=description,
            frame=frame,
            camera_id=self.camera_id
        )
    
    def _draw_student_boxes(self, frame, recognized_students):
        """
        Draw bounding boxes with student names (like the example code)
        Style: Green boxes for known students, Red for unknown
        """
        for sid, name, (top, right, bottom, left), confidence in recognized_students:
            # Set color based on recognition
            if sid == "unknown":
                color = (0, 0, 255)  # Red for unknown (BGR format)
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
        """Draw detected objects on frame"""
        for obj in objects:
            x1, y1, x2, y2 = obj.get("bbox", [0, 0, 0, 0])
            label = obj.get("class", "")
            confidence = obj.get("confidence", 0.0)
            
            # Draw box
            color = (0, 0, 255) if label in ["cell phone", "book", "laptop"] else (255, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label_text = f"{label} {int(confidence*100)}%"
            cv2.putText(frame, label_text, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame
    
    def _add_camera_overlay(self, frame, students):
        """Add camera information overlay"""
        h, w = frame.shape[:2]
        
        # Semi-transparent overlay at top
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 40), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)
        
        # Camera name
        cv2.putText(frame, f"{self.camera_name}", (10, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (w - 200, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Student count
        known_count = sum(1 for s in students if s[0] != "unknown")
        cv2.putText(frame, f"Students: {known_count}", (10, h - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)


def start_classroom_monitoring():
    """Start classroom monitoring with multiple cameras"""
    logger.info("🏫 Starting Classroom Monitoring System...")
    
    # Load camera configuration
    config_path = "config/cameras.yaml"
    
    if not os.path.exists(config_path):
        logger.error(f"❌ Camera configuration not found: {config_path}")
        print("\n❌ Error: config/cameras.yaml not found!")
        print("Please create the configuration file first.")
        input("\nPress Enter to return to menu...")
        return
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"❌ Error reading camera config: {e}")
        print(f"\n❌ Error reading configuration: {e}")
        input("\nPress Enter to return to menu...")
        return
    
    cameras = config.get("cameras", [])
    
    if not cameras:
        logger.error("❌ No cameras configured in cameras.yaml")
        print("\n❌ No cameras configured!")
        print("Please add cameras to config/cameras.yaml")
        input("\nPress Enter to return to menu...")
        return
    
    # Initialize violation logger
    violation_logger = ViolationLogger()
    
    # Create camera monitors
    camera_monitors = []
    threads = []
    
    for cam_config in cameras:
        cam_monitor = ClassroomCamera(cam_config, violation_logger)
        camera_monitors.append(cam_monitor)
    
    # Start all cameras
    print(f"\n🎥 Starting {len(camera_monitors)} camera(s)...")
    print("Press 'q' on any camera window to stop monitoring\n")
    
    for monitor in camera_monitors:
        thread = monitor.start()
        threads.append(thread)
    
    # Wait for threads
    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        logger.info("⚠️  Monitoring interrupted by user")
    
    # Stop all cameras
    for monitor in camera_monitors:
        monitor.stop()
    
    cv2.destroyAllWindows()
    logger.info("✅ Classroom monitoring stopped")
    
    print("\n✅ Monitoring session ended")
    input("Press Enter to return to menu...")


if __name__ == "__main__":
    start_classroom_monitoring()
