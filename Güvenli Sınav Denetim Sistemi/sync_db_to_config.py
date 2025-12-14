"""
Sync students from backend SQLite DB into config/students.yaml

Run this script from the project root (Güvenli Sınav Denetim Sistemi):

    python sync_db_to_config.py

This will read students from `backend/sinav_guvenlik.db` and overwrite
`config/students.yaml` with a list of students the frontend uses.
"""
import sqlite3
import yaml
import os

DB_PATH = os.path.join('backend', 'sinav_guvenlik.db')
CFG_PATH = os.path.join('config', 'students.yaml')

def read_students_from_db(db_path):
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT student_id, full_name, email FROM students ORDER BY id")
        rows = cursor.fetchall()
        students = []
        for r in rows:
            sid, name, email = r
            students.append({
                'id': sid,
                'name': name,
                'email': email,
                # Leave photo empty so existing workflow can be used to add photos
                'photo': ''
            })
        return students
    except Exception as e:
        print(f"❌ Error reading DB: {e}")
        return []
    finally:
        conn.close()

def write_config(students, cfg_path):
    os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
    data = {'students': students}
    with open(cfg_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    print(f"✅ Wrote {len(students)} students to: {cfg_path}")

if __name__ == '__main__':
    students = read_students_from_db(DB_PATH)
    if not students:
        print('⚠️  No students found in DB or failed to read DB.')
    write_config(students, CFG_PATH)
