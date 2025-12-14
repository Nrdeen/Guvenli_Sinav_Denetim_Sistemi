"""
Database connection configuration
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# استخدام SQLite بدلاً من MySQL لسهولة الاستخدام
# يمكن التبديل إلى MySQL لاحقاً عند الحاجة
USE_SQLITE = os.getenv("USE_SQLITE", "true").lower() == "true"

if USE_SQLITE:
    # استخدام SQLite (لا يحتاج تثبيت أو خادم منفصل)
    DATABASE_URL = "sqlite:///./sinav_guvenlik.db"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # مطلوب لـ SQLite
        pool_pre_ping=True,
        echo=False
    )
else:
    # استخدام MySQL (يحتاج MySQL Server مثبت ومشغل)
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "sinav_guvenlik_sistemi")
    
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False
    )

# إنشاء الجلسة
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# القاعدة للنماذج
from models import Base

def get_db():
    """
    Dependency للحصول على جلسة قاعدة البيانات
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()