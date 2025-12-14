"""
SQLAlchemy Models for Güvenli Sınav System
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Teacher(Base):
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    exams = relationship("Exam", back_populates="teacher")

class Exam(Base):
    __tablename__ = "exams"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    exam_name = Column(String(200), nullable=False)
    exam_code = Column(String(50), unique=True, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    status = Column(String(20), default='scheduled')
    exam_url = Column(String(500), nullable=True)
    exam_instructions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    teacher = relationship("Teacher", back_populates="exams")
    registrations = relationship("ExamRegistration", back_populates="exam")
    sessions = relationship("ActiveSession", back_populates="exam")
    violations = relationship("Violation", back_populates="exam")

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    registrations = relationship("ExamRegistration", back_populates="student")
    sessions = relationship("ActiveSession", back_populates="student")
    violations = relationship("Violation", back_populates="student")

class ExamRegistration(Base):
    __tablename__ = "exam_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    registered_at = Column(DateTime, default=datetime.now)
    status = Column(String(20), default='registered')  # 'registered', 'in_progress', 'completed', 'absent'
    
    exam = relationship("Exam", back_populates="registrations")
    student = relationship("Student", back_populates="registrations")

class ActiveSession(Base):
    __tablename__ = "active_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    session_start = Column(DateTime, nullable=False)
    last_heartbeat = Column(DateTime, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    is_active = Column(Boolean, default=True)
    
    exam = relationship("Exam", back_populates="sessions")
    student = relationship("Student", back_populates="sessions")
    violations = relationship("Violation", back_populates="session")
    stats = relationship("StudentStats", back_populates="session", uselist=False)

class Violation(Base):
    __tablename__ = "violations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("active_sessions.id"))
    exam_id = Column(Integer, ForeignKey("exams.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    violation_type = Column(String(50), nullable=False)  # 'face_not_detected', 'multiple_faces', 'looking_away', etc.
    severity = Column(String(20), default='medium')  # 'low', 'medium', 'high', 'critical'
    description = Column(Text)
    confidence_score = Column(Float)
    timestamp = Column(DateTime, nullable=False)
    screenshot_path = Column(String(500))
    
    session = relationship("ActiveSession", back_populates="violations")
    exam = relationship("Exam", back_populates="violations")
    student = relationship("Student", back_populates="violations")

class StudentStats(Base):
    __tablename__ = "student_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("active_sessions.id"))
    exam_id = Column(Integer, ForeignKey("exams.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    total_violations = Column(Integer, default=0)
    face_violations = Column(Integer, default=0)
    eye_violations = Column(Integer, default=0)
    mouth_violations = Column(Integer, default=0)
    multi_face_violations = Column(Integer, default=0)
    object_violations = Column(Integer, default=0)
    audio_violations = Column(Integer, default=0)
    tab_switches = Column(Integer, default=0)
    last_updated = Column(DateTime, nullable=False)
    
    session = relationship("ActiveSession", back_populates="stats")
