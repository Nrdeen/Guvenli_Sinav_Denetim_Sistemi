-- قاعدة بيانات نظام المراقبة الأونلاين
-- Online Exam Monitoring System Database

CREATE DATABASE IF NOT EXISTS sinav_guvenlik_sistemi
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE sinav_guvenlik_sistemi;

-- جدول الأساتذة/المراقبين
CREATE TABLE IF NOT EXISTS teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول الاختبارات
CREATE TABLE IF NOT EXISTS exams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    exam_name VARCHAR(200) NOT NULL,
    exam_code VARCHAR(50) UNIQUE NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    duration_minutes INT NOT NULL,
    status ENUM('scheduled', 'active', 'completed', 'cancelled') DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    INDEX idx_exam_code (exam_code),
    INDEX idx_status (status),
    INDEX idx_start_time (start_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول الطلاب
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_student_id (student_id),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول تسجيل الطلاب في الاختبارات
CREATE TABLE IF NOT EXISTS exam_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    student_id INT NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('registered', 'in_progress', 'completed', 'absent') DEFAULT 'registered',
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY unique_exam_student (exam_id, student_id),
    INDEX idx_exam_id (exam_id),
    INDEX idx_student_id (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول الجلسات النشطة (Active Sessions)
CREATE TABLE IF NOT EXISTS active_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    student_id INT NOT NULL,
    session_start DATETIME NOT NULL,
    last_heartbeat DATETIME NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    INDEX idx_exam_student (exam_id, student_id),
    INDEX idx_is_active (is_active),
    INDEX idx_last_heartbeat (last_heartbeat)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول الانتهاكات
CREATE TABLE IF NOT EXISTS violations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    exam_id INT NOT NULL,
    student_id INT NOT NULL,
    violation_type ENUM(
        'face_not_detected',
        'multiple_faces',
        'looking_away',
        'eye_closed',
        'mouth_open',
        'phone_detected',
        'book_detected',
        'person_detected',
        'audio_detected',
        'tab_switch',
        'window_focus_lost'
    ) NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    description TEXT,
    confidence_score FLOAT,
    timestamp DATETIME NOT NULL,
    screenshot_path VARCHAR(500),
    FOREIGN KEY (session_id) REFERENCES active_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    INDEX idx_session (session_id),
    INDEX idx_exam (exam_id),
    INDEX idx_student (student_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_violation_type (violation_type),
    INDEX idx_severity (severity)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول إحصائيات الطلاب الحية
CREATE TABLE IF NOT EXISTS student_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL,
    exam_id INT NOT NULL,
    student_id INT NOT NULL,
    total_violations INT DEFAULT 0,
    face_violations INT DEFAULT 0,
    eye_violations INT DEFAULT 0,
    mouth_violations INT DEFAULT 0,
    multi_face_violations INT DEFAULT 0,
    object_violations INT DEFAULT 0,
    audio_violations INT DEFAULT 0,
    tab_switches INT DEFAULT 0,
    last_updated DATETIME NOT NULL,
    FOREIGN KEY (session_id) REFERENCES active_sessions(id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY unique_session_stats (session_id),
    INDEX idx_exam (exam_id),
    INDEX idx_last_updated (last_updated)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول التنبيهات للمراقب
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    student_id INT NOT NULL,
    alert_type ENUM('high_violation_count', 'critical_violation', 'connection_lost', 'suspicious_activity') NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    INDEX idx_exam (exam_id),
    INDEX idx_is_read (is_read),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- جدول سجل النظام
CREATE TABLE IF NOT EXISTS system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT,
    student_id INT,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE SET NULL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE SET NULL,
    INDEX idx_timestamp (timestamp),
    INDEX idx_action (action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- بيانات تجريبية للأستاذة (كلمة المرور: admin123)
INSERT INTO teachers (username, password_hash, full_name, email) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lMjnYPJvPvOm', 'الأستاذة سارة أحمد', 'admin@example.com');

-- بيانات تجريبية لاختبار
INSERT INTO exams (teacher_id, exam_name, exam_code, start_time, end_time, duration_minutes, status) VALUES
(1, 'اختبار البرمجة النهائي', 'PROG2025', NOW(), DATE_ADD(NOW(), INTERVAL 2 HOUR), 120, 'active');

-- بيانات تجريبية للطلاب
INSERT INTO students (student_id, full_name, email) VALUES
('STU001', 'أحمد محمد علي', 'ahmad@student.edu'),
('STU002', 'فاطمة حسن', 'fatima@student.edu'),
('STU003', 'محمد خالد', 'mohamed@student.edu'),
('STU004', 'سارة يوسف', 'sara@student.edu'),
('STU005', 'عمر إبراهيم', 'omar@student.edu');

-- تسجيل الطلاب في الاختبار
INSERT INTO exam_registrations (exam_id, student_id, status) VALUES
(1, 1, 'registered'),
(1, 2, 'registered'),
(1, 3, 'registered'),
(1, 4, 'registered'),
(1, 5, 'registered');
