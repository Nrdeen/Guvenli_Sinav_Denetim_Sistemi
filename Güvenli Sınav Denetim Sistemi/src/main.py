import cv2
import yaml
from datetime import datetime
from pathlib import Path
from detection.face_detection import FaceDetector
from detection.eye_tracking import EyeTracker
from detection.mouth_detection import MouthMonitor
from detection.object_detection import ObjectDetector
from detection.multi_face import MultiFaceDetector
# from detection.audio_detection import AudioMonitor  # Disabled - requires webrtcvad
from utils.video_utils import VideoRecorder
from utils.screen_capture import ScreenRecorder
from utils.logging import AlertLogger
from utils.alert_system import AlertSystem
from utils.violation_logger import ViolationLogger
from utils.screenshot_utils import ViolationCapturer
# from reporting.report_generator import ReportGenerator  # Disabled temporarily

BASE_DIR = Path(__file__).resolve().parents[1]


def load_config():
    config_path = BASE_DIR / 'config' / 'config.yaml'
    with open(config_path) as f:
        return yaml.safe_load(f)

def display_detection_results(frame, results):
    y_offset = 30
    line_height = 30
    
    # Gaze direction translation
    gaze_tr = {
        'Center': 'merkez',
        'Left': 'sol',
        'Right': 'sag',
        'Up': 'yukari',
        'Down': 'asagi'
    }
    gaze_text = gaze_tr.get(results['gaze_direction'], results['gaze_direction'])
    
    # Status indicators in Turkish
    status_items = [
        f"Yuz: {'Mevcut' if results['face_present'] else 'Yok'}",
        f"Bakis: {gaze_text}",
        f"Gozler: {'Acik' if results['eye_ratio'] > 0.25 else 'Kapali'}",
        f"Agiz: {'Hareket Ediyor' if results['mouth_moving'] else 'Sabit'}",
        f"Nesne: {'Algilandi' if results['objects_detected'] else 'Yok'}"
    ]
    
    # Alert indicators in Turkish
    alert_items = []
    if results['multiple_faces']:
        alert_items.append("⚠️ Birden Fazla Yuz Algilandi!")
    if results['objects_detected']:
        alert_items.append("⚠️ Supheli Nesne Algilandi!")

    # Display status
    for item in status_items:
        cv2.putText(frame, item, (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        y_offset += line_height
    
    # Display alerts
    for item in alert_items:
        cv2.putText(frame, item, (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        y_offset += line_height
    
    # Timestamp
    cv2.putText(frame, results['timestamp'], 
               (frame.shape[1] - 250, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

def main():
    config = load_config()
    alert_logger = AlertLogger(config)
    alert_system = AlertSystem(config)
    violation_capturer = ViolationCapturer(config)
    violation_logger = ViolationLogger(config)
    # report_generator = ReportGenerator(config)  # Disabled temporarily

    student_info = {
        'id': 'STUDENT_001',
        'name': 'John Doe',
        'exam': 'Final Examination',
        'course': 'Computer Science 101'
    }

    # Create directory for shared frames at project root
    frame_path = BASE_DIR / 'logs' / 'current_frame.jpg'
    frame_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize recorders
    video_recorder = VideoRecorder(config)
    screen_recorder = ScreenRecorder(config)
    
    # Audio monitoring disabled - requires webrtcvad build tools
    # audio_monitor = AudioMonitor(config)
    # audio_monitor.alert_system = alert_system
    # audio_monitor.alert_logger = alert_logger

    # if config['detection']['audio_monitoring']['enabled']:
    #     audio_monitor.start()

    try:
        if config['screen']['recording']:
            screen_recorder.start_recording()
        # Initialize detectors
        detectors = [
            FaceDetector(config),
            EyeTracker(config),
            MouthMonitor(config),
            MultiFaceDetector(config),
            ObjectDetector(config),
        ]
        
        for detector in detectors:
            if hasattr(detector, 'set_alert_logger'):
                detector.set_alert_logger(alert_logger)

        # Start webcam recording
        video_recorder.start_recording()
        cap = cv2.VideoCapture(config['video']['source'])
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['video']['resolution'][0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['video']['resolution'][1])
        
        # Create fullscreen window
        cv2.namedWindow('Exam Proctoring', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('Exam Proctoring', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            results = {
                'face_present': False,
                'gaze_direction': 'Center',
                'eye_ratio': 0.3,
                'mouth_moving': False,
                'multiple_faces': False,
                'objects_detected': False,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Perform detections
            results['face_present'] = detectors[0].detect_face(frame)
            results['gaze_direction'], results['eye_ratio'] = detectors[1].track_eyes(frame)
            results['mouth_moving'] = detectors[2].monitor_mouth(frame)
            results['multiple_faces'] = detectors[3].detect_multiple_faces(frame)
            results['objects_detected'] = detectors[4].detect_objects(frame)

            if not results['face_present']:
                violation_type = "FACE_DISAPPEARED"
                alert_system.speak_alert(violation_type)
                
                # Capture and log violation
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                violation_image = violation_capturer.capture_violation(frame, violation_type, timestamp)
                violation_logger.log_violation(
                    violation_type,
                    timestamp,
                    {'duration': '5+ seconds', 'frame': results}
                )
                # alert_system.speak_alert("FACE_DISAPPEARED")
            elif results['multiple_faces']:
                violation_type = "MULTIPLE_FACES"
                alert_system.speak_alert(violation_type)
                
                # Capture and log violation
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                violation_image = violation_capturer.capture_violation(frame, violation_type, timestamp)
                violation_logger.log_violation(
                    violation_type,
                    timestamp,
                    {'duration': '5+ seconds', 'frame': results}
                )
                # alert_system.speak_alert("MULTIPLE_FACES")
            elif results['objects_detected']:
                violation_type = "OBJECT_DETECTED"
                alert_system.speak_alert(violation_type)
                
                # Capture and log violation
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                violation_image = violation_capturer.capture_violation(frame, violation_type, timestamp)
                violation_logger.log_violation(
                    violation_type,
                    timestamp,
                    {'duration': '5+ seconds', 'frame': results}
                )
                # alert_system.speak_alert("OBJECT_DETECTED")
            # elif results['gaze_direction'] != "Center":
            #     violation_type = "GAZE_AWAY"
            #     alert_system.speak_alert(violation_type)
                
            #     # Capture and log violation
            #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            #     violation_image = violation_capturer.capture_violation(frame, violation_type, timestamp)
            #     violation_logger.log_violation(
            #         violation_type,
            #         timestamp,
            #         {'duration': '5+ seconds', 'frame': results}
            #     )
                # alert_system.speak_alert("GAZE_AWAY")
            elif results['mouth_moving']:
                violation_type = "MOUTH_MOVING"
                alert_system.speak_alert(violation_type)
                
                # Capture and log violation
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                violation_image = violation_capturer.capture_violation(frame, violation_type, timestamp)
                violation_logger.log_violation(
                    violation_type,
                    timestamp,
                    {'duration': '5+ seconds', 'frame': results}
                )
                # alert_system.speak_alert("MOUTH_MOVING")

            
            # Display and record
            display_detection_results(frame, results)
            video_recorder.record_frame(frame)
            
            # Save current frame for dashboard streaming
            try:
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                with open(frame_path, 'wb') as f:
                    f.write(buffer.tobytes())
            except Exception as e:
                print(f"Error saving frame for streaming: {e}")
            
            # Show preview
            cv2.imshow('Exam Proctoring', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        violations = violation_logger.get_violations()
        # report_path = report_generator.generate_report(student_info, violations)
        # print(f"Report generated: {report_path}")
        print(f"Violations logged: {len(violations)}")
        if config['screen']['recording']:
            screen_data = screen_recorder.stop_recording()
            print(f"Screen recording saved: {screen_data['filename']}")
        
        video_data = video_recorder.stop_recording()
        print(f"Webcam recording saved: {video_data['filename']}")
        
        if cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()