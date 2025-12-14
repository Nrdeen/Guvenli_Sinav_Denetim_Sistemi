import reflex as rx
from typing import TypedDict, List
import cv2
import base64
import numpy as np
import asyncio
import os
import time
from datetime import datetime
from typing import List, Dict
from object_cheating.utils.eye_tracker import EyeTracker
from ultralytics import YOLO
from object_cheating.states.threshold_state import ThresholdState
import mediapipe as mp
import mss
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("Warning: face_recognition library not available. Face recognition features will be disabled.")
from object_cheating.states.students_state import StudentsState

class DetectionResult(TypedDict):
    id: int
    x: int
    y: int
    width: int
    height: int

class CameraState(ThresholdState):
    # Model state
    active_model: int = 1  # Contoh definisi state variable
    capture_mode: str = "camera"  # "camera" or "screen"
    
    # Stats panel
    detection_count: int = 0
    processing_time: float = 0.0
    
    # Behaviour panel
    highest_confidence_class: str = "N/A"
    highest_confidence: float = 0.0
    
    # Coordinate panel
    highest_conf_xmin: int = 0
    highest_conf_ymin: int = 0
    highest_conf_xmax: int = 0
    highest_conf_ymax: int = 0
    
    # Table panel
    table_data: List[Dict[str, str]] = []
    
    # Add table color mapping
    table_color_map: Dict[str, str] = {
        "cheating": "tomato",
        "left": "orange",
        "right": "orange",
        "Look Around": "violet",
        "Normal": "grass",
        "normal": "grass",
        "center": "green",
        "Bend Over The Desk": "cyan",
        "Hand Under Table": "indigo",
        "Stand Up": "sky",
        "Wave": "pink",
        "Phone Detected": "tomato",
    }
    
    # Constants for frame capture
    FRAME_CAPTURE_INTERVAL = 10  # Capture every 10th frame
    MAX_SAVES_PER_MINUTE = 6  # Maximum 6 saves per minute (1 every 10 seconds)
    
    # Add timestamp tracking for rate limiting
    _last_save_time: float = 0
    
    @rx.event
    def prev_model(self):
        if self.active_model > 1:
            self.active_model -= 1
            # Set default thresholds for the new model
            self.set_model_defaults(self.active_model)

    @rx.event
    def next_model(self):
        if self.active_model < 3:  # Ganti 3 dengan jumlah maksimum model Anda
            self.active_model += 1
            # Set default thresholds for the new model
            self.set_model_defaults(self.active_model)
    
    @rx.event
    def toggle_capture_mode(self):
        """Toggle between camera and screen capture"""
        if self.capture_mode == "camera":
            self.capture_mode = "screen"
        else:
            self.capture_mode = "camera"
        print(f"[DEBUG] Capture mode changed to: {self.capture_mode}")
    
    # Add new state variables for dialog
    show_warning_dialog: bool = False
    target_model: int = 0  # To store the model we want to switch to
    
    @rx.event
    async def try_change_model(self, target: int):
        """Try to change model, show warning if detection is enabled"""
        if self.detection_enabled:
            self.target_model = target
            self.show_warning_dialog = True
        else:
            # If detection is disabled, change model directly
            self.active_model = target
            self.selected_target = "All"
            # Set default thresholds for new model
            self.set_model_defaults(target)
                
    @rx.event
    async def close_warning_dialog(self):
        """Close the warning dialog without changing model"""
        self.show_warning_dialog = False
        self.target_model = 0
        
    # Add new state variables for delete dialog
    show_delete_dialog: bool = False
    
    @rx.event
    async def try_clear_camera(self):
        """Show confirmation dialog before clearing"""
        self.show_delete_dialog = True
    
    @rx.event
    async def confirm_clear(self):
        """Confirm and execute clear operation"""
        self.show_delete_dialog = False
        return CameraState.clear_camera
    
    @rx.event
    async def cancel_clear(self):
        """Cancel clear operation"""
        self.show_delete_dialog = False
            
    detection_enabled: bool = False
    eye_alerts: list[str] = []
    
    # Eye tracking state
    eye_alert_counter: int = 0
    eye_frame_counter: int = 0
    
    _original_frame_bytes: bytes = b""
    
    # Stream state
    camera_active: bool = False
    processing_active: bool = False
    current_frame: str = ""  # Base64 encoded image
    error_message: str = ""
    
    # Camera selection
    selected_camera_index: int = 0
    available_cameras: list[dict] = []
    
    # Tambahkan state untuk upload gambar
    uploaded_image: str = ""  # Untuk menyimpan gambar yang diupload
    
    video_playing: bool = False
    video_path: str = ""
    # Face detection state
    face_detection_active: bool = False
    detection_results: List[DetectionResult] = []
    min_neighbors: int = 5
    scale_factor: float = 1.3
    
    # Performance metrics
    fps: float = 0.0
    frame_count: int = 0
    last_frame_time: float = 0.0
    face_count: int = 0
    
    # Model YOLO
    _yolo_model = None
    
    selected_target: str = "All"
    
    # Add new YOLO model for Model 2
    _yolo_model_2 = None
    
    # MediaPipe pose detector for Model 1
    _pose_detector = None
    
    @classmethod
    def get_pose_detector(cls):
        """Get or initialize MediaPipe pose detector"""
        if cls._pose_detector is None:
            mp_pose = mp.solutions.pose
            cls._pose_detector = mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=0.3  # Lower threshold
            )
        return cls._pose_detector
    
    @classmethod
    def classify_pose(cls, landmarks):
        """Classify pose based on MediaPipe landmarks"""
        if not landmarks:
            return "Normal"
        
        mp_pose = mp.solutions.pose
        
        # Get key points
        nose = landmarks[mp_pose.PoseLandmark.NOSE]
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
        right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
        left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
        right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
        right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
        
        # Calculate average positions
        shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
        hip_y = (left_hip.y + right_hip.y) / 2
        knee_y = (left_knee.y + right_knee.y) / 2
        ankle_y = (left_ankle.y + right_ankle.y) / 2
        
        # Bend Over The Desk: head significantly below shoulders
        if nose.y > shoulder_y + 0.15:
            return "Bend Over The Desk"
        
        # Hand Under Table: wrist below hips
        if left_wrist.y > hip_y + 0.1 or right_wrist.y > hip_y + 0.1:
            return "Hand Under Table"
        
        # Stand Up: ankles significantly above knees (standing)
        if ankle_y < knee_y - 0.15:
            return "Stand Up"
        
        # Look Around: check head orientation (simple check)
        shoulder_x = (left_shoulder.x + right_shoulder.x) / 2
        if abs(nose.x - shoulder_x) > 0.1:
            return "Look Around"
        
        # Wave: check if arm is raised (elbow above shoulder)
        if left_elbow.y < left_shoulder.y - 0.1 or right_elbow.y < right_shoulder.y - 0.1:
            return "Wave"
        
        # Default to Normal
        return "Normal"
    
    def _apply_pose_detection(self, frame):
        """Apply MediaPipe pose detection and YOLO object detection"""
        start_time = time.time()
        
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Get pose detector
        pose_detector = self.get_pose_detector()
        
        # Process frame
        results = pose_detector.process(rgb_frame)
        
        print(f"[DEBUG] Pose results: {results.pose_landmarks is not None}")
        
        processed_frame = frame.copy()
        total_detections = 0
        highest_conf = 0.0
        highest_class = "Normal"
        coords = {"xmin": 0, "ymin": 0, "xmax": 0, "ymax": 0}
        all_detections = []
        selected_target = self.selected_target
        
        # First, check for objects using YOLO
        try:
            yolo_model = YOLO("Güvenli Sınav Denetim Sistemi/models/yolov8n.pt")
            obj_results = yolo_model(frame, conf=0.1, verbose=False)  # Lower confidence
            phone_detected = False
            for obj_result in obj_results:
                for box in obj_result.boxes:
                    cls = int(box.cls)
                    if cls == 67:  # cell phone
                        phone_detected = True
                        conf = float(box.conf[0])
                        print(f"[DEBUG] Phone detected with conf {conf:.3f}")
                        x1, y1, x2, y2 = box.xyxy[0]
                        cv2.rectangle(processed_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                        cv2.putText(processed_frame, f"Phone {conf:.2f}", (int(x1), int(y1)-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                        break
                if phone_detected:
                    break
            if not phone_detected:
                print("[DEBUG] No phone detected")
        except Exception as e:
            print(f"[DEBUG] Object detection failed: {e}")
            phone_detected = False
        
        if phone_detected:
            behavior = "Phone Detected"
            total_detections = 1
            highest_conf = 0.9
            highest_class = behavior
            coords = {"xmin": 0, "ymin": 0, "xmax": frame.shape[1], "ymax": frame.shape[0]}  # Full frame
            all_detections.append({
                "class_name": behavior,
                "conf": highest_conf,
                "coords": coords
            })
        elif results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # Classify the pose
            behavior = self.classify_pose(landmarks)
            
            # Filter by selected target
            if selected_target != "All" and behavior != selected_target:
                behavior = "Normal"  # Or skip detection
            
            # Get bounding box from pose landmarks
            x_coords = [lm.x for lm in landmarks]
            y_coords = [lm.y for lm in landmarks]
            
            xmin = int(min(x_coords) * frame.shape[1])
            xmax = int(max(x_coords) * frame.shape[1])
            ymin = int(min(y_coords) * frame.shape[0])
            ymax = int(max(y_coords) * frame.shape[0])
            
            # Draw bounding box
            cv2.rectangle(processed_frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            cv2.putText(processed_frame, behavior, (xmin, ymin - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            total_detections = 1
            highest_conf = 0.9  # MediaPipe confidence
            highest_class = behavior
            coords = {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}
            
            all_detections.append({
                "class_name": behavior,
                "conf": highest_conf,
                "coords": coords
            })
        
        process_time = time.time() - start_time
        
        return processed_frame, total_detections, process_time, highest_class, highest_conf, coords, all_detections
    
    @classmethod
    def get_yolo_model(cls):
        """Get or initialize YOLO model"""
        if cls._yolo_model is None:
            print("[DEBUG] Loading Model 1 (modelv11.pt)...")
            cls._yolo_model = YOLO("object_cheating/models/modelv11.pt")
            print(f"[DEBUG] Model 1 loaded. Classes: {cls._yolo_model.names}")
        return cls._yolo_model
    
    @classmethod
    def get_yolo_model_2(cls):
        """Get or initialize YOLO model 2 for cheating detection"""
        if cls._yolo_model_2 is None:
            cls._yolo_model_2 = YOLO("object_cheating/models/modelv8-2.pt")
        return cls._yolo_model_2
    
    @classmethod
    def get_class_color(cls, class_name: str) -> tuple:
        """Get color for each class in Model 1"""
        color_map = {
            "Normal": (0, 255, 128),        # Green
            "Bend Over The Desk": (255, 255, 0),    # Aqua
            "Hand Under Table": (255, 105, 65),      # Royal Blue
            "Look Around": (238, 130, 238),         # Violet
            "Stand Up": (250, 230, 230),           # Lavender
            "Wave": (193, 182, 255)                # Light Pink
        }
        return color_map.get(class_name, (0, 255, 128))  # Default to green if class not found
    
    def __init__(self, *args, **kwargs):
        """Initialize state with parent initialization."""
        super().__init__(*args, **kwargs)
        # Auto-detect cameras on initialization
        self.detect_cameras()
    
    @rx.event
    async def auto_start_camera(self):
        """Auto-start camera after detecting cameras"""
        # First detect cameras if not already detected
        if not self.available_cameras:
            self.detect_cameras()
        
        # Don't auto-start camera - let user start it manually
        # This prevents the camera from starting automatically on page load
        print(f"[DEBUG] Cameras detected: {len(self.available_cameras)}. Camera will start when user clicks the button.")
        
    @rx.event
    def set_active_model(self, model_num: int):
        if 1 <= model_num <= 3:
            self.active_model = model_num
        else:
            print(f"Nomor model tidak valid: {model_num}. Harus antara 1 dan 3.")
        
    
    def get_frame(self, cap):
        """Get frame from camera or screen based on capture mode"""
        if self.capture_mode == "screen":
            try:
                with mss.mss() as sct:
                    monitor = sct.monitors[1]  # Primary monitor
                    screenshot = sct.grab(monitor)
                    frame = np.frombuffer(screenshot.bgra, dtype=np.uint8)
                    frame = frame.reshape((monitor["height"], monitor["width"], 4))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                    return True, frame
            except Exception as e:
                print(f"[DEBUG] Failed to capture screen: {e}")
                return False, None
        else:
            return cap.read()

    @rx.event
    def set_camera_index(self, index: int):
        """Set the selected camera index"""
        self.selected_camera_index = index
        # If camera is active, restart it with new camera
        if self.camera_active:
            self.camera_active = False
            return CameraState.toggle_camera
    
    @rx.event
    def toggle_camera(self):
        self.camera_active = not self.camera_active
        print(f"[DEBUG] Camera toggled. New state: camera_active={self.camera_active}")
        if self.camera_active:
            print(f"[DEBUG] Starting camera with index {self.selected_camera_index}")
            return CameraState.process_camera_feed
        else:
            print(f"[DEBUG] Stopping camera")
            self.current_frame = ""
    
    @rx.event
    def detect_cameras(self):
        """Detect all available cameras and auto-select Logitech - Silent mode"""
        cameras = []
        logitech_index = None
        
        # Try up to 10 camera indices with DirectShow backend for Windows
        for i in range(10):
            # Try with DirectShow first (better for Windows)
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if not cap.isOpened():
                # Fallback to default backend
                cap = cv2.VideoCapture(i)
            
            if cap.isOpened():
                # Set reasonable defaults
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                
                # Get camera info
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                # Get camera name
                camera_name = f"Camera {i}"
                try:
                    backend = cap.getBackendName()
                    camera_name = f"Camera {i} - {width}x{height} ({backend})"
                except:
                    camera_name = f"Camera {i} - {width}x{height}"
                
                cameras.append({
                    "index": i,
                    "name": camera_name
                })
                
                # Check if this is a Logitech camera
                # Logitech cameras usually have higher resolution (720p or 1080p)
                if logitech_index is None and (width >= 1280 or height >= 720):
                    logitech_index = i
                
                cap.release()
                # Small delay to ensure camera is properly released
                import time
                time.sleep(0.1)
        
        self.available_cameras = cameras
        
        # Auto-select Logitech camera if found, otherwise use the last camera (usually external)
        # NO error_message - silent auto-selection
        if logitech_index is not None:
            self.selected_camera_index = logitech_index
        elif cameras:
            # Select the last camera (usually external camera, not laptop camera)
            self.selected_camera_index = cameras[-1]["index"]
        
        # Clear any error messages
        self.error_message = ""
        
        print(f"[DEBUG] Detected {len(cameras)} camera(s). Selected index: {self.selected_camera_index}")
            
    @property
    def original_frame(self) -> np.ndarray:
        """Convert bytes back to numpy array when needed"""
        if not self._original_frame_bytes:
            return None
        nparr = np.frombuffer(self._original_frame_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    def set_original_frame(self, frame: np.ndarray):
        """Convert numpy array to bytes for storage"""
        if frame is None:
            self._original_frame_bytes = b""
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            self._original_frame_bytes = buffer.tobytes()
            
    @rx.event
    async def save_current_frame(self):
        """Save the current frame as an image."""
        try:
            if not self.current_frame:
                self.error_message = "No frame to save."
                return

            header, encoded = self.current_frame.split(",", 1)
            image_data = base64.b64decode(encoded)

            save_dir = os.path.join("saved_frames", datetime.now().strftime("%Y-%m-%d"))
            os.makedirs(save_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%H-%M-%S")
            filename = f"{timestamp}.jpg"
            filepath = os.path.join(save_dir, filename)
            with open(filepath, "wb") as f:
                f.write(image_data)
                
            return rx.toast.success(
                f"Frame saved to {filepath}.", position="bottom-right"
            )

        except Exception as e:
            self.error_message = f"Error saving frame: {str(e)}"
            
    @rx.event
    def set_selected_target(self, target: str):
        """Set the selected target class."""
        self.selected_target = target
            
    def _apply_yolo_prediction(self, model, frame, is_model_1=True):
        """Helper method to apply YOLO prediction with current thresholds"""
        start_time = time.time()
        
        # Debug: Print current thresholds
        print(f"[DEBUG] Model: {'1' if is_model_1 else '2'}, Conf: {self.confidence_threshold}, IOU: {self.iou_threshold}")
        
        # Run prediction
        results = model(
            frame,
            conf=self.confidence_threshold,
            iou=self.iou_threshold
        )
        
        processed_frame = frame.copy()
        total_detections = 0
        highest_conf = 0.0
        highest_class = "N/A"
        coords = {"xmin": 0, "ymin": 0, "xmax": 0, "ymax": 0}
        all_detections = []
        selected_target = self.selected_target
        # First pass: Count all detections and draw boxes
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                conf = float(box.conf[0])
                cls = box.cls[0]
                class_name = model.names[int(cls)]
                
                # Filter detections based on selected target
                if selected_target != "All" and class_name != selected_target:
                    continue
                
                total_detections += 1
                
                # Simpan setiap deteksi
                detection = {
                    "class_name": class_name,
                    "conf": conf,
                    "coords": {
                        "xmin": int(x1),
                        "ymin": int(y1),
                        "xmax": int(x2),
                        "ymax": int(y2),
                    }
                }
                all_detections.append(detection)
                
                # Track highest confidence detection
                if conf > highest_conf:
                    highest_conf = conf
                    highest_class = class_name
                    coords["xmin"] = int(x1)
                    coords["ymin"] = int(y1)
                    coords["xmax"] = int(x2)
                    coords["ymax"] = int(y2)
                
                # Draw detection regardless of selected target
                label = f"{class_name} {conf:.2f}"
                
                if is_model_1:
                    color = self.get_class_color(class_name)
                else:
                    color = (71, 99, 255) if class_name == "cheating" else (0, 252, 124)
                
                # Convert coordinates to integers
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                
                # Draw bounding box and label
                cv2.rectangle(processed_frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(processed_frame, label, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Calculate runtime
        end_time = time.time()
        process_time = round((end_time - start_time), 1)
        
        # Debug output
        print(f"[DEBUG] Total detections: {total_detections}, Process time: {process_time}s")
        if total_detections > 0:
            print(f"[DEBUG] Highest: {highest_class} ({highest_conf:.2f})")
        else:
            print(f"[DEBUG] No detections found. Check if model is loaded correctly.")
        
        return processed_frame, total_detections, process_time, highest_class, round(highest_conf * 100), coords, all_detections
    
    def add_table_entry(self, location_file: str, behaviour: str, coordinate: str):
        """Add a new entry to the table with consecutive numbering."""
        new_entry = {
            "no": str(len(self.table_data) + 1),
            "location_file": location_file,
            "behaviour": behaviour,
            "coordinate": coordinate,
        }
        self.table_data.append(new_entry)  # Append to maintain chronological order
        print(f"Added entry to table_data: {new_entry}")
    
    async def _save_detection_image(self, frame, model_num: int, detections: list):
        """Save each detected bounding box as a separate cropped image."""
        try:
            # Create directory structure: detections/YYYY-MM-DD/Model_X/
            current_date = datetime.now().strftime("%Y-%m-%d")
            model_folder = f"Model_{model_num}"
            base_dir = os.path.join("detections", current_date, model_folder)
            os.makedirs(base_dir, exist_ok=True)
            
            # Generate unique timestamp for this batch of detections
            timestamp = datetime.now().strftime("%H-%M-%S")
            base_filename = f"{timestamp}.jpg"
            
            # Process each detection
            for idx, detection in enumerate(detections):
                class_name = detection["class_name"]
                coords = detection["coords"]
                x1, y1, x2, y2 = coords["xmin"], coords["ymin"], coords["xmax"], coords["ymax"]
                
                # Ensure coordinates are within image bounds
                height, width = frame.shape[:2]
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(width, x2)
                y2 = min(height, y2)
                
                if x2 <= x1 or y2 <= y1:
                    print(f"Invalid bounding box for {class_name}: skipping save")
                    continue
                
                # Crop the bounding box area
                cropped_image = frame[y1:y2, x1:x2]
                
                # Generate unique filename for each detection
                filename = f"{timestamp}_{idx}.jpg"
                filepath = os.path.join(base_dir, filename)
                
                # Save the cropped image
                cv2.imwrite(filepath, cropped_image)
                print(f"Saved cropped detection image to: {filepath}")
                
                # Add entry to table within context manager
                coordinate = f"[{x1},{y1},{x2},{y2}]"
                async with self:
                    new_entry = {
                        "no": str(len(self.table_data) + 1),  # Consecutive numbering
                        "location_file": os.path.join("detections", current_date, model_folder, filename),
                        "behaviour": class_name,
                        "coordinate": coordinate,
                    }
                    # Append to end instead of insert at beginning
                    self.table_data.append(new_entry)
                    print(f"Added entry to table_data: {new_entry}")
                    
        except Exception as e:
            print(f"Error in _save_detection_image: {str(e)}")
            
    async def _should_save_detection(self) -> bool:
        """Check if we should save based on rate limiting."""
        current_time = time.time()
        
        # Check if enough time has passed since last save (rate limiting)
        if current_time - self._last_save_time < (60 / self.MAX_SAVES_PER_MINUTE):
            print(f"Rate limiting: Not saving. Time since last save: {current_time - self._last_save_time:.2f} seconds")
            return False
            
        async with self:
            self._last_save_time = current_time
            print(f"Updated last save time: {self._last_save_time}")
            
        return True
    
    @rx.event
    async def handle_image_upload(self, files: list[rx.UploadFile]):
        """Handle image upload from local computer."""
        try:
            if not files or len(files) == 0:
                return

            file = files[0]
            upload_data = await file.read()
            
            # Convert image bytes to numpy array
            nparr = np.frombuffer(upload_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Store original frame using the new method
            self.set_original_frame(frame)
            
            # Convert to base64 for display
            img_base64 = base64.b64encode(upload_data).decode('utf-8')
            content_type = file.content_type or "image/jpeg"
            
            # Update state
            self.uploaded_image = f"data:{content_type};base64,{img_base64}"
            self.current_frame = self.uploaded_image
            self.camera_active = False
            
            # Proses gambar jika deteksi aktif
            if self.detection_enabled:
                return CameraState.process_uploaded_image
            
        except Exception as e:
            self.error_message = f"Upload error: {str(e)}"
                
    @rx.event
    async def toggle_detection(self, enabled: bool):
        """Toggle detection and process uploaded image if exists"""
        # Set state without async with
        self.detection_enabled = enabled
        self.eye_alerts = []
        self.eye_alert_counter = 0
        self.eye_frame_counter = 0
        
        if enabled and self._original_frame_bytes:
            # If enabled, process image with detection
            return CameraState.process_uploaded_image
        elif not enabled and self.uploaded_image:
            # If disabled, restore original uploaded image
            self.current_frame = self.uploaded_image

    @rx.event(background=True)
    async def process_uploaded_image(self):
        """Process uploaded image with selected model detection"""
        try:
            frame = self.original_frame
            if frame is None:
                return
            
            processed_frame = frame.copy()

            if self.detection_enabled:
                if self.active_model == 1:
                    # Model 1: MediaPipe pose detection for classroom behavior
                    processed_frame, total_detections, process_time, highest_class, highest_conf, coords, all_detections = self._apply_pose_detection(frame)
                    
                    if total_detections > 0:
                        await self._save_detection_image(frame, self.active_model, all_detections)
                    
                    # Update stats inside context manager
                    async with self:
                        self.detection_count = total_detections
                        self.processing_time = process_time
                        self.highest_confidence_class = highest_class
                        self.highest_confidence = highest_conf
                        self.highest_conf_xmin = coords["xmin"]
                        self.highest_conf_ymin = coords["ymin"]
                        self.highest_conf_xmax = coords["xmax"]
                        self.highest_conf_ymax = coords["ymax"]
                
                elif self.active_model == 2:
                    # Model 2: YOLOv8 for cheating detection
                    yolo_model = self.get_yolo_model_2()
                    processed_frame, total_detections, process_time, highest_class, highest_conf, coords, all_detections = self._apply_yolo_prediction(yolo_model, frame, False)
                    
                    if total_detections > 0:
                        await self._save_detection_image(frame, self.active_model, all_detections)
                    
                    # Update stats inside context manager
                    async with self:
                        self.detection_count = total_detections
                        self.processing_time = process_time
                        self.highest_confidence_class = highest_class
                        self.highest_confidence = highest_conf
                        self.highest_conf_xmin = coords["xmin"]
                        self.highest_conf_ymin = coords["ymin"]
                        self.highest_conf_xmax = coords["xmax"]
                        self.highest_conf_ymax = coords["ymax"]
                
                elif self.active_model == 3:
                # Model 3: Eye tracking with current thresholds
                    eye_tracker = EyeTracker()
                    try:
                        processed_frame, alerts, total_detections, process_time, highest_class, highest_conf, coords = eye_tracker.process_eye_detections(
                            processed_frame,
                            0,
                            0,
                            cnn_threshold=self.confidence_threshold,  # Use threshold from settings
                            duration_threshold=self.duration_threshold, 
                            is_video=False,
                            selected_target=self.selected_target
                        )
                        
                        # Add automatic capture for eye tracking
                        if total_detections > 0:
                            all_detections = [{
                                "class_name": highest_class,
                                "coords": coords
                            }]
                            # Modify all_detections to include student names
                            if recognized_names:
                                if len(recognized_names) == 1:
                                    student_name = recognized_names[0]
                                    for detection in all_detections:
                                        detection["class_name"] = f"{student_name}: {detection['class_name']}"
                                elif len(recognized_names) > 1:
                                    for detection in all_detections:
                                        detection["class_name"] = f"Multiple Students: {detection['class_name']}"
                            await self._save_detection_image(frame, self.active_model, all_detections)

                        # Update stats
                        async with self:
                            self.detection_count = total_detections
                            self.processing_time = process_time
                            self.highest_confidence_class = highest_class
                            self.highest_confidence = highest_conf 
                            self.highest_conf_xmin = coords["xmin"]
                            self.highest_conf_ymin = coords["ymin"]
                            self.highest_conf_xmax = coords["xmax"]
                            self.highest_conf_ymax = coords["ymax"]
                            if alerts:
                                self.eye_alerts = alerts
                    except Exception as e:
                        print(f"Eye tracking error: {str(e)}")
                        async with self:
                            self.detection_count = 0
                            self.processing_time = 0.0
                            self.highest_confidence_class = "N/A"
                            self.highest_confidence = 0
            
            # Convert processed frame to base64
            _, buffer = cv2.imencode('.jpg', processed_frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Update display
            async with self:
                self.current_frame = f"data:image/jpeg;base64,{img_base64}"
        
        except Exception as e:
            print(f"Image processing error: {str(e)}")
            async with self:
                self.error_message = f"Image processing error: {str(e)}"

    @rx.event
    async def handle_video_upload(self, files: list[rx.UploadFile]):
        """Handle video upload."""
        try:
            if not files or len(files) == 0:
                return

            file = files[0]
            upload_data = await file.read()
            
            # Save video to temporary file
            self.video_path = os.path.join(rx.get_upload_dir(), file.name)  # Use .name instead of .filename
            with open(self.video_path, "wb") as f:
                f.write(upload_data)
            
            # Stop other media sources and start video processing
            self.camera_active = False
            self.uploaded_image = ""
            self.current_frame = ""
            self.video_playing = True
            self.detection_enabled = False  # Reset detection state
            self.eye_alerts = []  # Clear any existing alerts
            
            return CameraState.process_video_frames
            
        except Exception as e:
            self.error_message = f"Video upload error: {str(e)}"

    @rx.event(background=True)
    async def process_video_frames(self):
        """Process and display video frames."""
        try:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                async with self:
                    self.error_message = "Failed to open video file"
                    self.video_playing = False
                return

            # Initialize trackers and models
            eye_tracker = None
            yolo_model = None
            yolo_model_2 = None
            frame_count = 0
            all_detections = []
            local_eye_alert_counter = 0
            local_eye_frame_counter = 0
            last_time = time.time()

            async with self:
                self.processing_active = True
                self.error_message = ""

            while self.video_playing and cap.isOpened():
                ret, frame = cap.read()
                if not ret:  # Reset video when it ends
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                frame_count += 1
                processed_frame = frame.copy()

                # Process detections if enabled
                if self.detection_enabled:
                    if self.active_model == 1:
                        # Model 1: YOLOv8 for classroom behavior
                        if yolo_model is None:
                            yolo_model = self.get_yolo_model()
                        processed_frame, total_detections, process_time, highest_class, highest_conf, coords, all_detections = self._apply_yolo_prediction(yolo_model, frame, True)
                            
                        # Only save on interval frames and with rate limiting
                        if total_detections > 0 and frame_count % self.FRAME_CAPTURE_INTERVAL == 0:
                            if await self._should_save_detection():
                                try:
                                    await self._save_detection_image(frame, self.active_model, all_detections)
                                except Exception as e:
                                    print(f"Error saving detection: {str(e)}")
                                
                        # Calculate FPS
                        current_time = time.time()
                        time_diff = current_time - last_time
                        current_fps = round(1.0 / time_diff, 1) if time_diff > 0 else 0.0
                        last_time = current_time

                        # Update stats
                        async with self:
                            self.detection_count = total_detections
                            self.processing_time = process_time
                            self.fps = current_fps  
                            self.highest_confidence_class = highest_class
                            self.highest_confidence = highest_conf
                            self.highest_conf_xmin = coords["xmin"]
                            self.highest_conf_ymin = coords["ymin"]
                            self.highest_conf_xmax = coords["xmax"]
                            self.highest_conf_ymax = coords["ymax"]

                    elif self.active_model == 2:
                        # Model 2: YOLOv8 for cheating detection
                        if yolo_model_2 is None:
                            yolo_model_2 = self.get_yolo_model_2()
                        processed_frame, total_detections, process_time, highest_class, highest_conf, coords, all_detections = self._apply_yolo_prediction(yolo_model_2, frame, False)

                        # Only save on interval frames and with rate limiting
                        if total_detections > 0 and frame_count % self.FRAME_CAPTURE_INTERVAL == 0:
                            if await self._should_save_detection():
                                try:
                                    await self._save_detection_image(frame, self.active_model, all_detections)
                                except Exception as e:
                                    print(f"Error saving detection: {str(e)}")
                                                            
                        # Calculate FPS
                        current_time = time.time()
                        time_diff = current_time - last_time
                        current_fps = round(1.0 / time_diff, 1) if time_diff > 0 else 0.0
                        last_time = current_time

                        # Update stats
                        async with self:
                            self.detection_count = total_detections
                            self.processing_time = process_time
                            self.fps = current_fps
                            self.highest_confidence_class = highest_class
                            self.highest_confidence = highest_conf
                            self.highest_conf_xmin = coords["xmin"]
                            self.highest_conf_ymin = coords["ymin"]
                            self.highest_conf_xmax = coords["xmax"]
                            self.highest_conf_ymax = coords["ymax"]

                    elif self.active_model == 3:
                        # Model 3: Eye tracking
                        if eye_tracker is None:
                            eye_tracker = EyeTracker()
                        
                        try:
                            processed_frame, alerts, total_detections, process_time, highest_class, highest_conf, coords = eye_tracker.process_eye_detections(
                                processed_frame,
                                local_eye_alert_counter,
                                local_eye_frame_counter,
                                cnn_threshold=self.confidence_threshold,
                                duration_threshold=self.duration_threshold,
                                is_video=True,
                                selected_target=self.selected_target
                            )
                            
                            # Add automatic capture for eye tracking with interval and rate limiting
                            if total_detections > 0 and frame_count % self.FRAME_CAPTURE_INTERVAL == 0:
                                if await self._should_save_detection():
                                    try:
                                        all_detections = [{
                                            "class_name": highest_class,
                                            "coords": coords
                                        }]
                                        await self._save_detection_image(frame, self.active_model, all_detections)
                                    except Exception as e:
                                        print(f"Error saving eye detection: {str(e)}")
                            
                            # Hitung FPS
                            current_time = time.time()
                            time_diff = current_time - last_time
                            current_fps = round(1.0 / time_diff, 1) if time_diff > 0 else 0.0
                            last_time = current_time

                            # Update stats
                            async with self:
                                self.detection_count = total_detections
                                self.processing_time = process_time
                                self.fps = current_fps
                                self.highest_confidence_class = highest_class
                                self.highest_confidence = highest_conf
                                self.highest_conf_xmin = coords["xmin"]
                                self.highest_conf_ymin = coords["ymin"]
                                self.highest_conf_xmax = coords["xmax"]
                                self.highest_conf_ymax = coords["ymax"]
                                if alerts:
                                    self.eye_alerts = alerts
                                    self.eye_alert_counter = local_eye_alert_counter
                                    self.eye_frame_counter = local_eye_frame_counter
                        except Exception as e:
                            print(f"Eye tracking error in video: {str(e)}")
                            async with self:
                                self.detection_count = 0
                                self.processing_time = 0.0
                                self.fps = 0.0

                # Convert frame to base64
                _, buffer = cv2.imencode('.jpg', processed_frame)
                img_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Update display
                async with self:
                    self.current_frame = f"data:image/jpeg;base64,{img_base64}"

                await asyncio.sleep(1/30)  # ~30 fps

            cap.release()
            
        except Exception as e:
            async with self:
                self.error_message = f"Video processing error: {str(e)}"
            
        finally:
            async with self:
                self.processing_active = False
                self.video_playing = False
                self.current_frame = ""

    @rx.event
    async def clear_camera(self):
        """Clear the camera state and stop the camera if it's running."""
        # First, disable detection to reset the switch state
        self.detection_enabled = False
        
        # Wait a brief moment for the switch to update
        await asyncio.sleep(0.1)
        
        # Then clear all other states
        self.camera_active = False
        self.video_playing = False 
        self.current_frame = ""
        self.uploaded_image = ""
        self._original_frame_bytes = b""  # Clear stored original frame
        self.detection_results = []
        self.face_count = 0
        self.error_message = ""
        self.eye_alerts = []
        self.eye_alert_counter = 0
        self.eye_frame_counter = 0
        self.detection_count = 0
        self.processing_time = 0.0
        self.fps = 0.0
        
        self.table_data: List[Dict[str, str]] = []
         
    @rx.event
    def toggle_face_detection(self):
        self.face_detection_active = not self.face_detection_active
        
    @rx.event
    def update_min_neighbors(self, value: str):
        self.min_neighbors = int(value)
        
    @rx.event
    def update_scale_factor(self, value: str):
        self.scale_factor = float(value) / 10

    @rx.event(background=True)
    async def process_camera_feed(self):
        """Process and display webcam frames."""
        print(f"[DEBUG] process_camera_feed started with camera index {self.selected_camera_index}")
        try:
            # Initialize camera with selected index and DirectShow backend for Windows
            print(f"[DEBUG] Opening camera with DirectShow...")
            cap = cv2.VideoCapture(self.selected_camera_index, cv2.CAP_DSHOW)
            
            # Set camera properties for better compatibility (optional)
            try:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)
            except Exception as e:
                print(f"[DEBUG] Could not set camera properties: {e}")
            
            if not cap.isOpened():
                print(f"[DEBUG] DirectShow failed, trying default backend...")
                # Try without DirectShow backend as fallback
                cap = cv2.VideoCapture(self.selected_camera_index)
                if not cap.isOpened():
                    print(f"[DEBUG] Failed to open camera with both backends")
                    async with self:
                        self.error_message = "فشل في فتح الكاميرا - Failed to open camera"
                        self.camera_active = False
                    return
            
            print(f"[DEBUG] Camera opened successfully! Starting frame processing...")
            
            # Small delay to ensure camera is ready
            await asyncio.sleep(0.5)

            # Initialize variables outside the loop
            eye_tracker = None
            yolo_model = None
            yolo_model_2 = None
            frame_count = 0
            all_detections = []
            local_eye_alert_counter = 0
            local_eye_frame_counter = 0
            last_time = time.time()

            async with self:
                self.processing_active = True
                self.error_message = ""
                print(f"[DEBUG] Processing active set to True, camera_active={self.camera_active}")

            while self.camera_active:
                ret, frame = self.get_frame(cap)
                if not ret:
                    print(f"[DEBUG] Failed to read frame - retrying...")
                    # Retry up to 3 times with small delay
                    for retry in range(3):
                        await asyncio.sleep(0.1)
                        ret, frame = self.get_frame(cap)
                        if ret:
                            print(f"[DEBUG] Frame read successful on retry {retry + 1}")
                            break
                        print(f"[DEBUG] Retry {retry + 1} failed")
                    
                    if not ret:
                        print(f"[DEBUG] Failed to read frame after retries")
                        async with self:
                            self.error_message = "فشل في قراءة الإطار - Failed to read frame"
                            self.camera_active = False
                            self.current_frame = ""  # Clear the frame immediately
                        break
                
                frame_count += 1
                if frame_count % 30 == 0:  # Print every 30 frames
                    print(f"[DEBUG] Processing frame {frame_count}, camera_active={self.camera_active}")
                
                processed_frame = frame.copy()

                # Face recognition
                recognized_names = []
                try:
                    from object_cheating.states.students_state import StudentsState
                    if hasattr(StudentsState, 'face_encodings') and StudentsState.face_encodings:
                        recognized_names = StudentsState.recognize_face(frame, StudentsState.face_encodings, StudentsState.face_names)
                except Exception as e:
                    print(f"Face recognition not available: {e}")

                # Process detections if enabled
                if self.detection_enabled:
                    if self.active_model == 1:
                        # Model 1: MediaPipe pose detection for classroom behavior
                        processed_frame, total_detections, process_time, highest_class, highest_conf, coords, all_detections = self._apply_pose_detection(frame)

                        # Modify all_detections to include student names
                        if recognized_names:
                            if len(recognized_names) == 1:
                                student_name = recognized_names[0]
                                for detection in all_detections:
                                    detection["class_name"] = f"{student_name}: {detection['class_name']}"
                            elif len(recognized_names) > 1:
                                for detection in all_detections:
                                    detection["class_name"] = f"Multiple Students: {detection['class_name']}"

                        if total_detections > 0 and frame_count % self.FRAME_CAPTURE_INTERVAL == 0:
                            if await self._should_save_detection():
                                try:
                                    await self._save_detection_image(frame, self.active_model, all_detections)
                                except Exception as e:
                                    print(f"Error saving detection: {str(e)}") 
                                                               
                        # Calculate FPS
                        current_time = time.time()
                        time_diff = current_time - last_time
                        current_fps = round(1.0 / time_diff, 1) if time_diff > 0 else 0.0
                        last_time = current_time

                        # Update stats
                        async with self:
                            self.detection_count = total_detections
                            self.processing_time = process_time
                            self.fps = current_fps 
                            
                            # Include student name if recognized
                            student_prefix = ""
                            if recognized_names:
                                if len(recognized_names) == 1:
                                    student_prefix = f"{recognized_names[0]}: "
                                else:
                                    student_prefix = f"Multiple Students: "
                            
                            self.highest_confidence_class = f"{student_prefix}{highest_class}"
                            self.highest_confidence = highest_conf
                            self.highest_conf_xmin = coords["xmin"]
                            self.highest_conf_ymin = coords["ymin"]
                            self.highest_conf_xmax = coords["xmax"]
                            self.highest_conf_ymax = coords["ymax"]
                            
                            if total_detections > 0:
                                table_entry = {
                                    "Time": datetime.now().strftime("%H:%M:%S"),
                                    "Class": highest_class,
                                    "Confidence": f"{highest_conf:.2f}",
                                    "X": coords["xmin"],
                                    "Y": coords["ymin"]
                                }
                                # Removed: self.table_data.append(table_entry)
                                # self.table_entry_counter += 1

                    elif self.active_model == 2:
                        # Model 2: YOLOv8 for cheating detection
                        if yolo_model_2 is None:
                            yolo_model_2 = self.get_yolo_model_2()
                        processed_frame, total_detections, process_time, highest_class, highest_conf, coords, all_detections = self._apply_yolo_prediction(yolo_model_2, frame, False)

                        # Modify all_detections to include student names
                        if recognized_names:
                            if len(recognized_names) == 1:
                                student_name = recognized_names[0]
                                for detection in all_detections:
                                    detection["class_name"] = f"{student_name}: {detection['class_name']}"
                            elif len(recognized_names) > 1:
                                for detection in all_detections:
                                    detection["class_name"] = f"Multiple Students: {detection['class_name']}"
                        
                        if total_detections > 0 and frame_count % self.FRAME_CAPTURE_INTERVAL == 0:
                            if await self._should_save_detection():
                                try:
                                    await self._save_detection_image(frame, self.active_model, all_detections)
                                except Exception as e:
                                    print(f"Error saving detection: {str(e)}")
                                    
                        # Calculate FPS
                        current_time = time.time()
                        time_diff = current_time - last_time
                        current_fps = round(1.0 / time_diff, 1) if time_diff > 0 else 0.0
                        last_time = current_time

                        # Update stats
                        async with self:
                            self.detection_count = total_detections
                            self.processing_time = process_time
                            self.fps = current_fps 
                            
                            # Include student name if recognized
                            student_prefix = ""
                            if recognized_names:
                                if len(recognized_names) == 1:
                                    student_prefix = f"{recognized_names[0]}: "
                                else:
                                    student_prefix = f"Multiple Students: "
                            
                            self.highest_confidence_class = f"{student_prefix}{highest_class}"
                            self.highest_confidence = highest_conf
                            self.highest_conf_xmin = coords["xmin"]
                            self.highest_conf_ymin = coords["ymin"]
                            self.highest_conf_xmax = coords["xmax"]
                            self.highest_conf_ymax = coords["ymax"]

                    elif self.active_model == 3:
                        # Model 3: Eye tracking
                        if eye_tracker is None:
                            eye_tracker = EyeTracker()
                        
                        try:
                            processed_frame, alerts, total_detections, process_time, highest_class, highest_conf, coords = eye_tracker.process_eye_detections(
                                processed_frame,
                                local_eye_alert_counter,
                                local_eye_frame_counter,
                                cnn_threshold=self.confidence_threshold,
                                duration_threshold=self.duration_threshold,
                                is_video=True,
                                selected_target=self.selected_target
                            )
                            
                            # Add automatic capture for eye tracking with interval and rate limiting
                            if total_detections > 0 and frame_count % self.FRAME_CAPTURE_INTERVAL == 0:
                                if await self._should_save_detection():
                                    try:
                                        all_detections = [{
                                            "class_name": highest_class,
                                            "coords": coords
                                        }]
                                        # Modify all_detections to include student names
                                        if recognized_names:
                                            if len(recognized_names) == 1:
                                                student_name = recognized_names[0]
                                                for detection in all_detections:
                                                    detection["class_name"] = f"{student_name}: {detection['class_name']}"
                                            elif len(recognized_names) > 1:
                                                for detection in all_detections:
                                                    detection["class_name"] = f"Multiple Students: {detection['class_name']}"
                                        await self._save_detection_image(frame, self.active_model, all_detections)
                                    except Exception as e:
                                        print(f"Error saving eye detection: {str(e)}")                            
                            
                            # Hitung FPS
                            current_time = time.time()
                            time_diff = current_time - last_time
                            current_fps = round(1.0 / time_diff, 1) if time_diff > 0 else 0.0
                            last_time = current_time

                            # Update stats
                            async with self:
                                self.detection_count = total_detections
                                self.processing_time = process_time
                                self.fps = current_fps
                                
                                # Include student name if recognized
                                student_prefix = ""
                                if recognized_names:
                                    if len(recognized_names) == 1:
                                        student_prefix = f"{recognized_names[0]}: "
                                    else:
                                        student_prefix = f"Multiple Students: "
                                
                                self.highest_confidence_class = f"{student_prefix}{highest_class}"
                                self.highest_confidence = highest_conf
                                self.highest_conf_xmin = coords["xmin"]
                                self.highest_conf_ymin = coords["ymin"]
                                self.highest_conf_xmax = coords["xmax"]
                                self.highest_conf_ymax = coords["ymax"]
                                if alerts:
                                    self.eye_alerts = alerts
                                    self.eye_alert_counter = local_eye_alert_counter
                                    self.eye_frame_counter = local_eye_frame_counter
                        except Exception as e:
                            print(f"Eye tracking error in video: {str(e)}")
                            async with self:
                                self.detection_count = 0
                                self.processing_time = 0.0
                                self.fps = 0.0

                # Convert and display frame
                try:
                    _, buffer = cv2.imencode('.jpg', processed_frame)
                    img_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    async with self:
                        self.current_frame = f"data:image/jpeg;base64,{img_base64}"
                        self.frame_count += 1
                except Exception as e:
                    print(f"[DEBUG] Error encoding frame: {e}")
                    async with self:
                        self.error_message = f"خطأ في تشفير الإطار - Frame encoding error: {str(e)}"
                        self.camera_active = False
                        self.current_frame = ""
                    break
                
                await asyncio.sleep(1/30)
                
        except Exception as e:
            async with self:
                self.error_message = f"Camera error: {str(e)}"
                self.camera_active = False
                self.processing_active = False
        
        finally:
            if 'cap' in locals():
                cap.release()
            async with self:
                self.processing_active = False
                self.detection_results = []
                # Only clear frame if camera is not active
                if not self.camera_active:
                    self.current_frame = ""
                print(f"[DEBUG] Camera feed stopped. camera_active={self.camera_active}")