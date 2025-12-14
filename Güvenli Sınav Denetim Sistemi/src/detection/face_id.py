"""
Face Recognition Module
Real-time student face recognition and identification
"""

import face_recognition
import cv2
import numpy as np
import logging
from src.utils.student_loader import load_students

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load known faces on module initialization
known_encodings, known_ids, known_names = load_students()

if len(known_encodings) == 0:
    logger.warning("⚠️  No student faces loaded! Please add student photos.")


def recognize_student(frame, tolerance=0.45):
    """
    Recognize students in a video frame
    
    Args:
        frame: BGR image from OpenCV
        tolerance: Face matching tolerance (lower is more strict)
        
    Returns:
        list: List of tuples (student_id, student_name, face_location, confidence)
    """
    if len(known_encodings) == 0:
        return []
    
    # Convert BGR to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Find all faces in the frame
    face_locations = face_recognition.face_locations(rgb)
    face_encs = face_recognition.face_encodings(rgb, face_locations)
    
    results = []
    
    for enc, loc in zip(face_encs, face_locations):
        # Compare with known faces
        matches = face_recognition.compare_faces(known_encodings, enc, tolerance=tolerance)
        distances = face_recognition.face_distance(known_encodings, enc)
        
        if len(distances) > 0:
            best_match_idx = np.argmin(distances)
            confidence = 1 - distances[best_match_idx]
            
            if matches[best_match_idx]:
                sid = known_ids[best_match_idx]
                sname = known_names[best_match_idx]
                results.append((sid, sname, loc, confidence))
            else:
                # Unknown person
                results.append(("unknown", "Unknown Person", loc, 0.0))
        else:
            results.append(("unknown", "Unknown Person", loc, 0.0))
    
    return results


def draw_face_boxes(frame, recognition_results):
    """
    Draw bounding boxes and names on the frame
    
    Args:
        frame: OpenCV image
        recognition_results: Results from recognize_student()
        
    Returns:
        frame: Annotated image
    """
    for sid, name, (top, right, bottom, left), confidence in recognition_results:
        # Choose color based on recognition
        if sid == "unknown":
            color = (0, 0, 255)  # Red for unknown
            label = "Unknown"
        else:
            color = (0, 255, 0)  # Green for known students
            label = f"{name} ({int(confidence*100)}%)"
        
        # Draw rectangle around face
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        
        # Draw label background
        cv2.rectangle(frame, (left, top - 35), (right, top), color, cv2.FILLED)
        
        # Draw label text
        cv2.putText(
            frame, 
            label,
            (left + 6, top - 10),
            cv2.FONT_HERSHEY_DUPLEX,
            0.6,
            (255, 255, 255),
            1
        )
        
        # Draw student ID
        if sid != "unknown":
            cv2.putText(
                frame,
                sid,
                (left + 6, bottom + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1
            )
    
    return frame


def get_primary_student(recognition_results):
    """
    Get the most confident/primary student from results
    
    Args:
        recognition_results: Results from recognize_student()
        
    Returns:
        tuple: (student_id, student_name) or ("unknown", "Unknown")
    """
    if not recognition_results:
        return ("unknown", "Unknown")
    
    # Filter out unknown faces
    known_students = [r for r in recognition_results if r[0] != "unknown"]
    
    if not known_students:
        return ("unknown", "Unknown")
    
    # Return the one with highest confidence
    best = max(known_students, key=lambda x: x[3])
    return (best[0], best[1])


def reload_students():
    """
    Reload student data (call this if students.yaml changes)
    """
    global known_encodings, known_ids, known_names
    
    logger.info("Reloading student data...")
    known_encodings, known_ids, known_names = load_students()
    logger.info(f"Reloaded {len(known_encodings)} students")


if __name__ == "__main__":
    # Test face recognition with webcam
    print("Testing Face Recognition (Press 'q' to quit)...")
    
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Recognize faces
        results = recognize_student(frame)
        
        # Draw boxes
        frame = draw_face_boxes(frame, results)
        
        # Display
        cv2.imshow("Face Recognition Test", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
