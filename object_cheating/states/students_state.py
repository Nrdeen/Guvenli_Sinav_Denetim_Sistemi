import reflex as rx
from typing import List, Dict
import sqlite3
import os
import cv2
import numpy as np
import base64
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("Warning: face_recognition library not available. Face recognition features will be disabled.")
from datetime import datetime

class Student:
    def __init__(self, id: int, name: str, student_id: str, photo_path: str = None, face_encoding = None):
        self.id = id
        self.name = name
        self.student_id = student_id
        self.photo_path = photo_path
        self.face_encoding = face_encoding

class StudentsState(rx.State):
    # Students list
    students: List[Dict] = []
    
    # Add student form
    new_student_name: str = ""
    new_student_id: str = ""
    uploaded_photo: str = ""
    
    # Face recognition
    face_encodings: List = []
    face_names: List[str] = []
    
    # Database path
    db_path: str = "students.db"
    
    def init_database(self):
        """Initialize SQLite database for students"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                student_id TEXT UNIQUE NOT NULL,
                photo_path TEXT,
                face_encoding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_students(self):
        """Load students from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, student_id, photo_path FROM students")
        rows = cursor.fetchall()
        
        self.students = [
            {
                "id": row[0],
                "name": row[1],
                "student_id": row[2],
                "photo_path": row[3]
            }
            for row in rows
        ]
        
        conn.close()
    
    def load_face_encodings(self):
        """Load face encodings for recognition"""
        if not FACE_RECOGNITION_AVAILABLE:
            return
            
        self.face_encodings = []
        self.face_names = []
        
        for student in self.students:
            if student["photo_path"] and os.path.exists(student["photo_path"]):
                try:
                    image = face_recognition.load_image_file(student["photo_path"])
                    encodings = face_recognition.face_encodings(image)
                    if encodings:
                        self.face_encodings.append(encodings[0])
                        self.face_names.append(student["name"])
                except Exception as e:
                    print(f"Error loading face encoding for {student['name']}: {e}")
    
    @rx.event
    def initialize_students(self):
        """Initialize database and load students - called on app start"""
        self.init_database()
        self.load_students()
        self.load_face_encodings()
        """Initialize SQLite database for students"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                student_id TEXT UNIQUE NOT NULL,
                photo_path TEXT,
                face_encoding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def load_students(self):
        """Load students from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, student_id, photo_path FROM students")
        rows = cursor.fetchall()
        
        self.students = [
            {
                "id": row[0],
                "name": row[1],
                "student_id": row[2],
                "photo_path": row[3]
            }
            for row in rows
        ]
        
        conn.close()
    
    def load_face_encodings(self):
        """Load face encodings for recognition"""
        if not FACE_RECOGNITION_AVAILABLE:
            return
            
        self.face_encodings = []
        self.face_names = []
        
        for student in self.students:
            if student["photo_path"] and os.path.exists(student["photo_path"]):
                try:
                    image = face_recognition.load_image_file(student["photo_path"])
                    encodings = face_recognition.face_encodings(image)
                    if encodings:
                        self.face_encodings.append(encodings[0])
                        self.face_names.append(student["name"])
                except Exception as e:
                    print(f"Error loading face encoding for {student['name']}: {e}")
    
    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        """Handle file upload for student photo"""
        if not files:
            return
        
        # Get the first file
        upload_file = files[0]
        
        # Read the file content
        upload_data = await upload_file.read()
        
        # Convert to base64 for storage
        self.uploaded_photo = f"data:image/jpeg;base64,{base64.b64encode(upload_data).decode()}"
        
        return rx.toast.success(f"Photo uploaded: {upload_file.name}")
    
    @rx.event
    def set_new_student_name(self, name: str):
        self.new_student_name = name
    
    @rx.event
    def set_new_student_id(self, student_id: str):
        self.new_student_id = student_id
    
    @rx.event
    def add_student(self):
        """Add new student to database"""
        # Initialize database if not done
        if not self.students:  # If no students loaded, initialize
            self.initialize_students()
            
        if not self.new_student_name or not self.new_student_id:
            return
        
        # Save photo if uploaded
        photo_path = None
        face_encoding = None
        
        if self.uploaded_photo:
            # Decode base64 image
            try:
                header, encoded = self.uploaded_photo.split(",", 1)
                image_data = base64.b64decode(encoded)
                
                # Save to assets/students_photos folder
                os.makedirs("assets/students_photos", exist_ok=True)
                photo_path = f"students_photos/{self.new_student_id}.jpg"
                
                with open(photo_path, "wb") as f:
                    f.write(image_data)
                
                # Generate face encoding
                if FACE_RECOGNITION_AVAILABLE:
                    image = face_recognition.load_image_file(photo_path)
                    encodings = face_recognition.face_encodings(image)
                    if encodings:
                        face_encoding = encodings[0].tobytes()
                    
            except Exception as e:
                print(f"Error processing photo: {e}")
        
        # Add to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR REPLACE INTO students (name, student_id, photo_path, face_encoding) VALUES (?, ?, ?, ?)",
            (self.new_student_name, self.new_student_id, photo_path, face_encoding)
        )
        
        conn.commit()
        conn.close()
        
        # Reset form
        self.new_student_name = ""
        self.new_student_id = ""
        self.uploaded_photo = ""
        
        # Reload students
        self.load_students()
        self.load_face_encodings()
    
    @rx.event
    def delete_student(self, student_id: int):
        """Delete student from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get photo path before deleting
        cursor.execute("SELECT photo_path FROM students WHERE id = ?", (student_id,))
        row = cursor.fetchone()
        if row and row[0]:
            try:
                os.remove(row[0])
            except:
                pass
        
        # Delete from database
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        
        conn.commit()
        conn.close()
        
        # Reload students
        self.load_students()
        self.load_face_encodings()
    
    @staticmethod
    def recognize_face(frame, face_encodings, face_names):
        """Recognize faces in frame and return student names"""
        if not FACE_RECOGNITION_AVAILABLE:
            return []
            
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find faces
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings_frame = face_recognition.face_encodings(rgb_frame, face_locations)
            
            recognized_names = []
            
            for face_encoding in face_encodings_frame:
                # Compare with known faces
                matches = face_recognition.compare_faces(face_encodings, face_encoding, tolerance=0.5)
                name = "Unknown"
                
                if True in matches:
                    first_match_index = matches.index(True)
                    name = face_names[first_match_index]
                
                recognized_names.append(name)
            
            return recognized_names
            
        except Exception as e:
            print(f"Face recognition error: {e}")
            return []