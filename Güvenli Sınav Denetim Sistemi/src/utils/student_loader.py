"""
Student Loader - Face Recognition Setup
Loads student data and prepares face encodings for recognition
"""

import face_recognition
import yaml
import cv2
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_students():
    """
    Load students from config/students.yaml and prepare face encodings
    
    Returns:
        tuple: (known_encodings, known_ids, known_names)
    """
    config_path = "config/students.yaml"
    
    if not os.path.exists(config_path):
        logger.error(f"❌ Configuration file not found: {config_path}")
        return [], [], []
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"❌ Error reading config file: {e}")
        return [], [], []
    
    if not data or "students" not in data:
        logger.error("❌ No students data found in config file")
        return [], [], []
    
    known_encodings = []
    known_ids = []
    known_names = []
    
    logger.info("Loading student face encodings...")
    
    for student in data["students"]:
        student_id = student.get("id", "unknown")
        student_name = student.get("name", "Unknown")
        img_path = student.get("photo", "")
        
        if not img_path:
            logger.warning(f"⚠️  No photo path for student: {student_name}")
            continue
        
        if not os.path.exists(img_path):
            logger.warning(f"⚠️  Photo not found: {img_path} for {student_name}")
            continue
        
        try:
            # Load image file
            image = face_recognition.load_image_file(img_path)
            
            # Extract face encoding
            enc = face_recognition.face_encodings(image)
            
            if len(enc) == 0:
                logger.warning(f"⚠️  No face detected in photo: {img_path} for {student_name}")
                continue
            
            if len(enc) > 1:
                logger.warning(f"⚠️  Multiple faces detected in: {img_path}. Using first face.")
            
            known_encodings.append(enc[0])
            known_ids.append(student_id)
            known_names.append(student_name)
            
            logger.info(f"✔️  Loaded: {student_name} ({student_id})")
            
        except Exception as e:
            logger.error(f"❌ Error processing {img_path} for {student_name}: {e}")
            continue
    
    logger.info(f"✅ Successfully loaded {len(known_encodings)} student(s)")
    
    return known_encodings, known_ids, known_names


def get_student_by_id(student_id):
    """
    Get student information by ID
    
    Args:
        student_id: Student ID to search for
        
    Returns:
        dict: Student data or None if not found
    """
    config_path = "config/students.yaml"
    
    if not os.path.exists(config_path):
        return None
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        if data and "students" in data:
            for student in data["students"]:
                if student.get("id") == student_id:
                    return student
    except Exception as e:
        logger.error(f"Error reading student data: {e}")
    
    return None


def list_all_students():
    """
    List all students from configuration
    
    Returns:
        list: List of student dictionaries
    """
    config_path = "config/students.yaml"
    
    if not os.path.exists(config_path):
        return []
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        if data and "students" in data:
            return data["students"]
    except Exception as e:
        logger.error(f"Error reading student data: {e}")
    
    return []


if __name__ == "__main__":
    # Test the loader
    print("Testing Student Loader...")
    encodings, ids, names = load_students()
    
    print(f"\nLoaded {len(encodings)} students:")
    for sid, name in zip(ids, names):
        print(f"  - {name} ({sid})")
