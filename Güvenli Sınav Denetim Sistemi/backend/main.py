"""
FastAPI Backend Server for Güvenli Sınav Monitoring System
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import json
import asyncio
from pydantic import BaseModel

from database import get_db, engine, Base, SessionLocal
import models

# إنشاء الجداول
Base.metadata.create_all(bind=engine)

# إنشاء معلم افتراضي إذا لم يكن موجوداً
def create_default_teacher():
    try:
        db = SessionLocal()
        teacher = db.query(models.Teacher).filter(models.Teacher.id == 1).first()
        if not teacher:
            default_teacher = models.Teacher(
                username="admin",
                password_hash="admin123",  # في الإنتاج يجب استخدام hashing
                full_name="المعلم الافتراضي",
                email="admin@example.com"
            )
            db.add(default_teacher)
            db.commit()
    except Exception as e:
        print(f"Error creating default teacher: {e}")
    finally:
        try:
            db.close()
        except:
            pass

create_default_teacher()

app = FastAPI(
    title="Güvenli Sınav API",
    description="نظام مراقبة الاختبارات الأونلاين",
    version="1.0.0"
)

# إعدادات CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# مدير الاتصالات WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}  # {exam_id: {student_id: websocket}}
        self.teacher_connections: dict = {}  # {exam_id: [websockets]}
    
    async def connect_student(self, websocket: WebSocket, exam_id: str, student_id: str):
        await websocket.accept()
        if exam_id not in self.active_connections:
            self.active_connections[exam_id] = {}
        self.active_connections[exam_id][student_id] = websocket
    
    async def connect_teacher(self, websocket: WebSocket, exam_id: str):
        await websocket.accept()
        if exam_id not in self.teacher_connections:
            self.teacher_connections[exam_id] = []
        self.teacher_connections[exam_id].append(websocket)
    
    def disconnect_student(self, exam_id: str, student_id: str):
        if exam_id in self.active_connections:
            self.active_connections[exam_id].pop(student_id, None)
    
    def disconnect_teacher(self, websocket: WebSocket, exam_id: str):
        if exam_id in self.teacher_connections:
            if websocket in self.teacher_connections[exam_id]:
                self.teacher_connections[exam_id].remove(websocket)
    
    async def broadcast_to_teachers(self, exam_id: str, message: dict):
        """إرسال رسالة لجميع المراقبين المتصلين بالاختبار"""
        if exam_id in self.teacher_connections:
            for connection in self.teacher_connections[exam_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()

# ==================== Pydantic Models ====================

class ViolationCreate(BaseModel):
    student_id: str
    exam_code: str
    violation_type: str
    severity: str = "medium"
    description: Optional[str] = None
    confidence_score: Optional[float] = None

class HeartbeatData(BaseModel):
    student_id: str
    exam_code: str
    is_active: bool = True

class ExamCreate(BaseModel):
    exam_name: str
    exam_code: str
    duration_minutes: int = 120
    exam_date: Optional[str] = None
    exam_url: Optional[str] = None
    exam_instructions: Optional[str] = None

class StudentCreate(BaseModel):
    student_id: str
    student_name: str
    student_email: Optional[str] = None
    exam_code: Optional[str] = None

class StudentStatus(BaseModel):
    student_id: str
    student_name: str
    is_active: bool
    total_violations: int
    last_heartbeat: datetime
    face_violations: int
    eye_violations: int
    mouth_violations: int
    multi_face_violations: int
    object_violations: int
    audio_violations: int

# ==================== HTTP Endpoints ====================

@app.get("/")
async def root():
    return {"message": "Güvenli Sınav API - نظام مراقبة الاختبارات الأونلاين"}

@app.get("/api/exams/{exam_code}/info")
async def get_exam_info(exam_code: str, db: Session = Depends(get_db)):
    """الحصول على معلومات الاختبار"""
    exam = db.query(models.Exam).filter(models.Exam.exam_code == exam_code.strip().upper()).first()
    if not exam:
        raise HTTPException(status_code=404, detail="الاختبار غير موجود")
    
    # الحصول على عدد الطلاب المسجلين
    registrations_count = db.query(models.ExamRegistration).filter(
        models.ExamRegistration.exam_id == exam.id
    ).count()
    
    return {
        "id": exam.id,
        "exam_name": exam.exam_name,
        "exam_code": exam.exam_code,
        "start_time": exam.start_time.isoformat() if exam.start_time else None,
        "end_time": exam.end_time.isoformat() if exam.end_time else None,
        "duration_minutes": exam.duration_minutes,
        "status": exam.status,
        "exam_url": exam.exam_url,
        "exam_instructions": exam.exam_instructions,
        "registered_students_count": registrations_count
    }

@app.post("/api/exams")
async def create_exam(exam: ExamCreate, db: Session = Depends(get_db)):
    """إنشاء اختبار جديد أو تحديث موجود"""
    try:
        # البحث عن الاختبار الموجود
        existing_exam = db.query(models.Exam).filter(models.Exam.exam_code == exam.exam_code.strip().upper()).first()
        
        if existing_exam:
            # تحديث الاختبار الموجود
            existing_exam.exam_name = exam.exam_name
            if exam.exam_date:
                from dateutil import parser
                start_time = parser.parse(exam.exam_date)
            else:
                start_time = datetime.now()
            existing_exam.start_time = start_time
            existing_exam.end_time = start_time + timedelta(minutes=exam.duration_minutes)
            existing_exam.duration_minutes = exam.duration_minutes
            existing_exam.exam_url = exam.exam_url
            existing_exam.exam_instructions = exam.exam_instructions
            existing_exam.status = 'scheduled'
            
            db.commit()
            db.refresh(existing_exam)
            
            return {
                "id": existing_exam.id,
                "exam_name": existing_exam.exam_name,
                "exam_code": existing_exam.exam_code,
                "message": "تم تحديث الاختبار بنجاح"
            }
        else:
            # إنشاء اختبار جديد
            if exam.exam_date:
                from dateutil import parser
                start_time = parser.parse(exam.exam_date)
            else:
                start_time = datetime.now()
            
            end_time = start_time + timedelta(minutes=exam.duration_minutes)
            
            # إنشاء الاختبار
            new_exam = models.Exam(
                teacher_id=1,  # مؤقتاً - يمكن ربطه بنظام المصادقة لاحقاً
                exam_name=exam.exam_name,
                exam_code=exam.exam_code.strip().upper(),
                start_time=start_time,
                end_time=end_time,
                duration_minutes=exam.duration_minutes,
                exam_url=exam.exam_url,
                exam_instructions=exam.exam_instructions,
                status='scheduled'
            )
            
            db.add(new_exam)
            db.commit()
            db.refresh(new_exam)
            
            return {
                "id": new_exam.id,
                "exam_name": new_exam.exam_name,
                "exam_code": new_exam.exam_code,
                "message": "تم إنشاء الاختبار بنجاح"
            }
    except Exception as e:
        print(f"Error creating/updating exam: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"خطأ في إنشاء/تحديث الاختبار: {str(e)}")

@app.post("/api/exams/{exam_code}/start")
async def start_exam(exam_code: str, db: Session = Depends(get_db)):
    """بدء الاختبار وإرسال إشارة للطلاب لبدء المراقبة"""
    exam = db.query(models.Exam).filter(models.Exam.exam_code == exam_code.strip().upper()).first()
    if not exam:
        raise HTTPException(status_code=404, detail="الاختبار غير موجود")
    
    # تحديث حالة الاختبار إلى "active"
    exam.status = "active"
    db.commit()
    
    # إرسال إشارة لبدء المراقبة لجميع الطلاب المتصلين
    await manager.broadcast_to_teachers(exam_code.upper(), {
        "type": "exam_started",
        "exam_code": exam_code.upper(),
        "message": "تم بدء الاختبار - يجب على الطلاب بدء المراقبة الآن"
    })
    
    return {
        "message": f"تم بدء الاختبار {exam_code} بنجاح",
        "exam_code": exam_code.upper(),
        "status": "active"
    }

@app.post("/api/students")
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """إضافة طالب جديد وتسجيله في الاختبار إذا تم تحديد exam_code"""
    # التحقق من وجود الطالب برقم الطالب
    existing_student_by_id = db.query(models.Student).filter(
        models.Student.student_id == student.student_id
    ).first()
    
    student_exists = False
    if existing_student_by_id:
        # الطالب موجود
        student_exists = True
        current_student = existing_student_by_id
    else:
        # التحقق من عدم تكرار البريد الإلكتروني
        student_email = student.student_email or f"{student.student_id}@example.com"
        existing_student_by_email = db.query(models.Student).filter(
            models.Student.email == student_email
        ).first()
        
        if existing_student_by_email:
            raise HTTPException(
                status_code=400, 
                detail=f"البريد الإلكتروني {student_email} مستخدم من قبل طالب آخر ({existing_student_by_email.student_id})"
            )
        
        # إنشاء الطالب الجديد
        new_student = models.Student(
            student_id=student.student_id.upper(),
            full_name=student.student_name,
            email=student_email
        )
        
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        current_student = new_student
    
    # إذا تم تحديد exam_code، قم بتسجيل الطالب في الاختبار
    registration_message = ""
    if student.exam_code:
        # البحث عن الاختبار
        exam = db.query(models.Exam).filter(
            models.Exam.exam_code == student.exam_code.strip().upper()
        ).first()
        
        if not exam:
            # إذا لم يكن الاختبار موجوداً، أنشئه تلقائياً
            exam = models.Exam(
                teacher_id=1,  # المعلم الافتراضي
                exam_name=f"اختبار {student.exam_code.strip().upper()}",
                exam_code=student.exam_code.strip().upper(),
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=2),
                duration_minutes=120,
                status='active'
            )
            db.add(exam)
            db.commit()
            db.refresh(exam)
        
        # التحقق من عدم تكرار التسجيل
        existing_registration = db.query(models.ExamRegistration).filter(
            models.ExamRegistration.exam_id == exam.id,
            models.ExamRegistration.student_id == current_student.id
        ).first()
        
        if not existing_registration:
            # تسجيل الطالب في الاختبار
            registration = models.ExamRegistration(
                exam_id=exam.id,
                student_id=current_student.id,
                status='registered'
            )
            db.add(registration)
            db.commit()
            registration_message = f" وتم تسجيله في اختبار {student.exam_code.upper()}"
        else:
            registration_message = f" (مسجل مسبقاً في اختبار {student.exam_code.upper()})"
    
    message = "الطالب موجود مسبقاً" if student_exists else "تم إضافة الطالب بنجاح"
    message += registration_message
    
    return {
        "id": current_student.id,
        "student_id": current_student.student_id,
        "full_name": current_student.full_name,
        "email": current_student.email,
        "message": message,
        "already_exists": student_exists
    }

@app.put("/api/students/{student_id}")
async def update_student(
    student_id: str, 
    student_update: StudentCreate, 
    db: Session = Depends(get_db)
):
    """تحديث بيانات طالب موجود"""
    # البحث عن الطالب
    existing_student = db.query(models.Student).filter(
        models.Student.student_id == student_id
    ).first()
    
    if not existing_student:
        raise HTTPException(status_code=404, detail="الطالب غير موجود")
    
    # التحقق من البريد الإلكتروني إذا تم تغييره
    new_email = student_update.student_email or f"{student_id}@example.com"
    if new_email != existing_student.email:
        email_conflict = db.query(models.Student).filter(
            models.Student.email == new_email,
            models.Student.id != existing_student.id
        ).first()
        
        if email_conflict:
            raise HTTPException(
                status_code=400,
                detail=f"البريد الإلكتروني {new_email} مستخدم من قبل طالب آخر"
            )
        
        existing_student.email = new_email
    
    # تحديث البيانات
    existing_student.full_name = student_update.student_name
    
    db.commit()
    db.refresh(existing_student)
    
    return {
        "id": existing_student.id,
        "student_id": existing_student.student_id,
        "full_name": existing_student.full_name,
        "email": existing_student.email,
        "message": "تم تحديث بيانات الطالب بنجاح"
    }

@app.delete("/api/students/{student_id}")
async def delete_student(student_id: str, db: Session = Depends(get_db)):
    """حذف طالب"""
    student = db.query(models.Student).filter(
        models.Student.student_id == student_id
    ).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="الطالب غير موجود")
    
    # حذف الطالب
    db.delete(student)
    db.commit()
    
    return {
        "message": f"تم حذف الطالب {student_id} بنجاح"
    }

@app.get("/api/students/all")
async def get_all_students(db: Session = Depends(get_db)):
    """الحصول على قائمة جميع الطلاب في قاعدة البيانات"""
    students = db.query(models.Student).all()
    
    students_list = []
    for student in students:
        # البحث عن الاختبارات المسجل فيها الطالب
        registrations = db.query(models.ExamRegistration).filter(
            models.ExamRegistration.student_id == student.id
        ).all()
        
        exam_codes = []
        for reg in registrations:
            exam = db.query(models.Exam).filter(models.Exam.id == reg.exam_id).first()
            if exam:
                exam_codes.append(exam.exam_code)
        
        students_list.append({
            "id": student.student_id,
            "name": student.full_name,
            "email": student.email,
            "exam_code": ", ".join(exam_codes) if exam_codes else "غير مسجل",
            "created_at": student.created_at.isoformat() if hasattr(student, 'created_at') and student.created_at else None
        })
    
    return students_list

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """الحصول على إحصائيات النظام الكاملة"""
    # عدد الأساتذة
    teachers_count = db.query(models.Teacher).count()
    teachers = db.query(models.Teacher).all()
    
    # عدد الاختبارات
    exams_count = db.query(models.Exam).count()
    exams = db.query(models.Exam).all()
    
    # عدد الطلاب
    students_count = db.query(models.Student).count()
    
    # عدد التسجيلات
    registrations_count = db.query(models.ExamRegistration).count()
    registrations = db.query(models.ExamRegistration).all()
    
    # عدد الجلسات النشطة
    active_sessions_count = db.query(models.ActiveSession).filter(
        models.ActiveSession.is_active == True
    ).count()
    active_sessions = db.query(models.ActiveSession).filter(
        models.ActiveSession.is_active == True
    ).all()
    
    # عدد الانتهاكات
    violations_count = db.query(models.Violation).count()
    violations = db.query(models.Violation).all()
    
    # تفاصيل الأساتذة
    teachers_list = [{
        "id": t.id,
        "username": t.username,
        "full_name": t.full_name,
        "email": t.email
    } for t in teachers]
    
    # تفاصيل الاختبارات
    exams_list = [{
        "id": e.id,
        "exam_name": e.exam_name,
        "exam_code": e.exam_code,
        "duration_minutes": e.duration_minutes,
        "status": e.status,
        "start_time": e.start_time.isoformat() if e.start_time else None,
        "end_time": e.end_time.isoformat() if e.end_time else None
    } for e in exams]
    
    # تفاصيل التسجيلات
    registrations_list = []
    for reg in registrations:
        student = db.query(models.Student).filter(models.Student.id == reg.student_id).first()
        exam = db.query(models.Exam).filter(models.Exam.id == reg.exam_id).first()
        if student and exam:
            registrations_list.append({
                "student_id": student.student_id,
                "student_name": student.full_name,
                "exam_code": exam.exam_code,
                "exam_name": exam.exam_name,
                "status": reg.status,
                "registered_at": reg.registered_at.isoformat() if reg.registered_at else None
            })
    
    # تفاصيل الجلسات النشطة
    sessions_list = []
    for session in active_sessions:
        student = db.query(models.Student).filter(models.Student.id == session.student_id).first()
        exam = db.query(models.Exam).filter(models.Exam.id == session.exam_id).first()
        if student and exam:
            sessions_list.append({
                "student_id": student.student_id,
                "student_name": student.full_name,
                "exam_code": exam.exam_code,
                "exam_name": exam.exam_name,
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "last_heartbeat": session.last_heartbeat.isoformat() if session.last_heartbeat else None
            })
    
    # تفاصيل الانتهاكات
    violations_list = []
    for violation in violations:
        student = db.query(models.Student).filter(models.Student.id == violation.student_id).first()
        exam = db.query(models.Exam).filter(models.Exam.id == violation.exam_id).first()
        if student and exam:
            violations_list.append({
                "student_id": student.student_id,
                "student_name": student.full_name,
                "exam_code": exam.exam_code,
                "violation_type": violation.violation_type,
                "severity": violation.severity,
                "description": violation.description,
                "detected_at": violation.detected_at.isoformat() if violation.detected_at else None
            })
    
    return {
        "summary": {
            "teachers_count": teachers_count,
            "exams_count": exams_count,
            "students_count": students_count,
            "registrations_count": registrations_count,
            "active_sessions_count": active_sessions_count,
            "violations_count": violations_count
        },
        "teachers": teachers_list,
        "exams": exams_list,
        "registrations": registrations_list,
        "active_sessions": sessions_list,
        "violations": violations_list
    }

@app.get("/api/exams/{exam_code}/verify-student/{student_id}")
async def verify_student_registration(exam_code: str, student_id: str, db: Session = Depends(get_db)):
    """التحقق من تسجيل الطالب في الاختبار"""
    # البحث عن الطالب
    student = db.query(models.Student).filter(models.Student.student_id == student_id.upper()).first()
    if not student:
        return {"registered": False, "message": "الطالب غير موجود في النظام"}
    
    # البحث عن الاختبار
    exam = db.query(models.Exam).filter(models.Exam.exam_code == exam_code.upper()).first()
    if not exam:
        return {"registered": False, "message": "الاختبار غير موجود"}
    
    # التحقق من التسجيل
    registration = db.query(models.ExamRegistration).filter(
        models.ExamRegistration.exam_id == exam.id,
        models.ExamRegistration.student_id == student.id
    ).first()
    
    if registration:
        return {
            "registered": True,
            "student_name": student.full_name,
            "exam_name": exam.exam_name,
            "exam_status": exam.status,
            "message": "الطالب مسجل في الاختبار"
        }
    else:
        return {"registered": False, "message": "الطالب غير مسجل في هذا الاختبار"}

@app.post("/api/violations")
async def create_violation(violation: ViolationCreate, db: Session = Depends(get_db)):
    """تسجيل انتهاك جديد"""
    # البحث عن الطالب والاختبار
    student = db.query(models.Student).filter(models.Student.student_id == violation.student_id).first()
    exam = db.query(models.Exam).filter(models.Exam.exam_code == violation.exam_code).first()
    
    if not student or not exam:
        raise HTTPException(status_code=404, detail="الطالب أو الاختبار غير موجود")
    
    # البحث عن الجلسة النشطة
    session = db.query(models.ActiveSession).filter(
        models.ActiveSession.exam_id == exam.id,
        models.ActiveSession.student_id == student.id,
        models.ActiveSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="لا توجد جلسة نشطة")
    
    # إنشاء الانتهاك
    new_violation = models.Violation(
        session_id=session.id,
        exam_id=exam.id,
        student_id=student.id,
        violation_type=violation.violation_type,
        severity=violation.severity,
        description=violation.description,
        confidence_score=violation.confidence_score,
        timestamp=datetime.now()
    )
    db.add(new_violation)
    
    # تحديث الإحصائيات
    stats = db.query(models.StudentStats).filter(models.StudentStats.session_id == session.id).first()
    if stats:
        stats.total_violations += 1
        if 'face' in violation.violation_type:
            stats.face_violations += 1
        elif 'eye' in violation.violation_type or 'looking' in violation.violation_type:
            stats.eye_violations += 1
        elif 'mouth' in violation.violation_type:
            stats.mouth_violations += 1
        elif 'multiple' in violation.violation_type:
            stats.multi_face_violations += 1
        elif 'phone' in violation.violation_type or 'book' in violation.violation_type or 'person' in violation.violation_type:
            stats.object_violations += 1
        elif 'audio' in violation.violation_type:
            stats.audio_violations += 1
        stats.last_updated = datetime.now()
    
    db.commit()
    
    # إرسال إشعار للمراقبين عبر WebSocket
    await manager.broadcast_to_teachers(exam.id, {
        "type": "new_violation",
        "student_id": student.student_id,
        "student_name": student.full_name,
        "violation_type": violation.violation_type,
        "severity": violation.severity,
        "timestamp": datetime.now().isoformat()
    })
    
    return {"status": "success", "violation_id": new_violation.id}

@app.post("/api/heartbeat")
async def heartbeat(data: HeartbeatData, db: Session = Depends(get_db)):
    """تحديث نبضات القلب للطالب"""
    student = db.query(models.Student).filter(models.Student.student_id == data.student_id).first()
    exam = db.query(models.Exam).filter(models.Exam.exam_code == data.exam_code).first()
    
    if not student or not exam:
        raise HTTPException(status_code=404, detail="الطالب أو الاختبار غير موجود")
    
    # تحديث أو إنشاء الجلسة
    session = db.query(models.ActiveSession).filter(
        models.ActiveSession.exam_id == exam.id,
        models.ActiveSession.student_id == student.id
    ).first()
    
    if not session:
        # إنشاء جلسة جديدة
        session = models.ActiveSession(
            exam_id=exam.id,
            student_id=student.id,
            session_start=datetime.now(),
            last_heartbeat=datetime.now(),
            is_active=True
        )
        db.add(session)
        db.flush()
        
        # إنشاء إحصائيات
        stats = models.StudentStats(
            session_id=session.id,
            exam_id=exam.id,
            student_id=student.id,
            last_updated=datetime.now()
        )
        db.add(stats)
    else:
        session.last_heartbeat = datetime.now()
        session.is_active = data.is_active
    
    db.commit()
    
    return {"status": "success"}

@app.get("/api/exams/{exam_code}/students", response_model=List[StudentStatus])
async def get_students_status(exam_code: str, db: Session = Depends(get_db)):
    """الحصول على حالة جميع الطلاب في الاختبار"""
    exam = db.query(models.Exam).filter(models.Exam.exam_code == exam_code).first()
    if not exam:
        raise HTTPException(status_code=404, detail="الاختبار غير موجود")
    
    # جلب جميع الطلاب المسجلين
    registrations = db.query(models.ExamRegistration).filter(
        models.ExamRegistration.exam_id == exam.id
    ).all()
    
    students_status = []
    for reg in registrations:
        student = reg.student
        session = db.query(models.ActiveSession).filter(
            models.ActiveSession.exam_id == exam.id,
            models.ActiveSession.student_id == student.id
        ).first()
        
        stats = None
        if session:
            stats = db.query(models.StudentStats).filter(
                models.StudentStats.session_id == session.id
            ).first()
        
        # التحقق من النشاط (آخر نبضة قلب خلال 30 ثانية)
        is_active = False
        last_heartbeat = None
        if session:
            last_heartbeat = session.last_heartbeat
            time_diff = datetime.now() - session.last_heartbeat
            is_active = time_diff.total_seconds() < 30 and session.is_active
        
        students_status.append({
            "student_id": student.student_id,
            "student_name": student.full_name,
            "is_active": is_active,
            "last_heartbeat": last_heartbeat or datetime.now(),
            "total_violations": stats.total_violations if stats else 0,
            "face_violations": stats.face_violations if stats else 0,
            "eye_violations": stats.eye_violations if stats else 0,
            "mouth_violations": stats.mouth_violations if stats else 0,
            "multi_face_violations": stats.multi_face_violations if stats else 0,
            "object_violations": stats.object_violations if stats else 0,
            "audio_violations": stats.audio_violations if stats else 0
        })
    
    return students_status

# ==================== WebSocket Endpoints ====================

@app.websocket("/ws/teacher/{exam_code}")
async def teacher_websocket(websocket: WebSocket, exam_code: str, db: Session = Depends(get_db)):
    """WebSocket للمراقب لاستقبال التحديثات الفورية"""
    exam = db.query(models.Exam).filter(models.Exam.exam_code == exam_code).first()
    if not exam:
        await websocket.close(code=1008)
        return
    
    await manager.connect_teacher(websocket, exam.id)
    
    try:
        while True:
            # إرسال تحديثات دورية كل 5 ثواني
            await asyncio.sleep(5)
            students_status = await get_students_status(exam_code, db)
            await websocket.send_json({
                "type": "students_update",
                "data": [s.dict() for s in students_status]
            })
    except WebSocketDisconnect:
        manager.disconnect_teacher(websocket, exam.id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
