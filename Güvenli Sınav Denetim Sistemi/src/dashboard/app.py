from flask import Flask, render_template, jsonify, request
import yaml
from datetime import datetime
from pathlib import Path
import json
import time
import os
import signal

app = Flask(__name__)

# Shutdown flag file
SHUTDOWN_FLAG_FILE = Path(__file__).resolve().parents[2] / '.shutdown_flag'

# Load configuration relative to project root
BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = BASE_DIR / 'config' / 'config.yaml'

with open(CONFIG_PATH) as f:
    config = yaml.safe_load(f)

# Active sessions tracking (in real implementation, use database)
active_sessions = {}

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/students')
def students():
    return render_template('students.html')

@app.route('/recordings')
def recordings():
    return render_template('recordings.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/alerts')
def alerts_page():
    return render_template('alerts.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/api/shutdown', methods=['POST'])
def shutdown_system():
    """Trigger system shutdown"""
    # Create shutdown flag file
    SHUTDOWN_FLAG_FILE.touch()
    
    # Shutdown Flask server
    def shutdown():
        os._exit(0)
    
    import threading
    threading.Timer(0.5, shutdown).start()
    
    return jsonify({'status': 'ok', 'message': 'System shutting down...'})

@app.route('/api/alerts')
def get_alerts():
    log_dir = Path(config['logging']['log_path'])
    if not log_dir.is_absolute():
        log_dir = BASE_DIR / log_dir
    log_file = log_dir / "alerts.log"
    alerts = []
    
    if log_file.exists():
        with open(log_file, 'r') as f:
            alerts = [line.strip() for line in f.readlines()[-10:]]  # Get last 10 alerts
            
    return jsonify(alerts)


@app.route('/api/students_list')
def students_list_api():
    """Return students loaded from `config/students.yaml` for the frontend to consume."""
    students_path = BASE_DIR / 'config' / 'students.yaml'
    students = []
    try:
        if students_path.exists():
            with open(students_path, 'r', encoding='utf-8') as f:
                students = yaml.safe_load(f) or []
    except Exception:
        students = []

    return jsonify(students)

@app.route('/api/stats')
def get_stats():
    """Dynamic stats based on actual running sessions"""
    # Read violations from logs
    log_dir = Path(config['logging']['log_path'])
    if not log_dir.is_absolute():
        log_dir = BASE_DIR / log_dir
    
    violations_file = log_dir / "violations.json"
    total_violations = 0
    students_data = []
    
    # Try to read violations data
    if violations_file.exists():
        try:
            with open(violations_file, 'r', encoding='utf-8') as f:
                violations_data = json.load(f)
                total_violations = len(violations_data)
        except:
            pass
    
    # Count active sessions (students currently being monitored)
    # In real implementation, track via database or session file
    num_students = len(active_sessions) if active_sessions else 1  # At least 1 if main.py running
    
    # Read recent alerts
    alerts_file = log_dir / "alerts.log"
    recent_alerts_count = 0
    if alerts_file.exists():
        with open(alerts_file, 'r') as f:
            lines = f.readlines()
            # Count alerts from last 5 minutes
            recent_alerts_count = min(len(lines), 10)
    
    # Generate camera monitoring data dynamically
    if active_sessions:
        camera_data = list(active_sessions.values())
    else:
        # Default data when system just started - one active camera
        camera_data = [
            {
                'camera': 'Camera_1',
                'status': 'Aktif',
                'violations': total_violations,
                'last_detection': datetime.now().strftime('%H:%M:%S')
            }
        ]
    
    return jsonify({
        'active_cameras': num_students,  # Number of active monitoring cameras
        'violations': total_violations,
        'real_time_alerts': recent_alerts_count,
        'risk_level': min(int(total_violations * 3), 100),  # Risk percentage
        'cameras_list': camera_data
    })

@app.route('/api/register_camera', methods=['POST'])
def register_camera():
    """Register a new camera/monitoring session"""
    from flask import request
    data = request.get_json()
    camera_id = data.get('id', f'camera_{len(active_sessions) + 1}')
    active_sessions[camera_id] = {
        'camera': camera_id,
        'status': 'Aktif',
        'violations': 0,
        'last_detection': datetime.now().strftime('%H:%M:%S')
    }
    return jsonify({'success': True, 'camera_id': camera_id})

@app.route('/api/update_detection', methods=['POST'])
def update_detection():
    """Update camera detection status"""
    from flask import request
    data = request.get_json()
    camera_id = data.get('id')
    if camera_id in active_sessions:
        active_sessions[camera_id]['status'] = data.get('status', 'Aktif')
        active_sessions[camera_id]['violations'] = data.get('violations', 0)
        active_sessions[camera_id]['last_detection'] = datetime.now().strftime('%H:%M:%S')
    return jsonify({'success': True})

@app.route('/api/config', methods=['GET', 'POST'])
def config_api():
    """Get or update configuration"""
    from flask import request
    
    if request.method == 'GET':
        # Return current config
        return jsonify(config)
    
    elif request.method == 'POST':
        # Update config
        try:
            new_settings = request.get_json()
            
            # Deep merge new settings into existing config
            def merge_dicts(base, updates):
                for key, value in updates.items():
                    if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                        merge_dicts(base[key], value)
                    else:
                        base[key] = value
            
            merge_dicts(config, new_settings)
            
            # Save updated config to file
            with open(CONFIG_PATH, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            return jsonify({'success': True, 'message': 'Configuration updated successfully'})
        
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/video_feed')
def video_feed():
    """Video streaming route - optimized for stable continuous streaming"""
    from flask import Response
    import cv2
    import os
    
    def generate():
        video_path = BASE_DIR / 'logs' / 'current_frame.jpg'
        last_frame = None
        last_mtime = 0
        
        while True:
            try:
                if video_path.exists():
                    # Check if file was modified
                    current_mtime = os.path.getmtime(video_path)
                    
                    if current_mtime != last_mtime:
                        # New frame available, read it
                        with open(video_path, 'rb') as f:
                            frame = f.read()
                        if frame and len(frame) > 100:  # Valid frame
                            last_frame = frame
                            last_mtime = current_mtime
                    
                    # Always yield the last valid frame
                    if last_frame:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + last_frame + b'\r\n')
                
                # Small delay to match ~30 FPS
                time.sleep(0.033)
                
            except Exception as e:
                # On error, keep streaming last valid frame
                if last_frame:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + last_frame + b'\r\n')
                time.sleep(0.05)
    
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame',
                    headers={
                        'Cache-Control': 'no-cache, no-store, must-revalidate',
                        'Pragma': 'no-cache',
                        'Expires': '0',
                        'Connection': 'keep-alive'
                    })

@app.route('/api/camera_status')
def camera_status():
    """Check if the main camera feed is active"""
    frame_path = BASE_DIR / 'logs' / 'current_frame.jpg'
    is_active = False
    last_update = None
    freshness_threshold = 15  # seconds
    
    if frame_path.exists():
        mtime = frame_path.stat().st_mtime
        last_update = datetime.fromtimestamp(mtime).strftime('%H:%M:%S')
        if time.time() - mtime <= freshness_threshold:
            is_active = True
    
    return jsonify({
        'active': is_active,
        'last_update': last_update
    })

@app.route('/api/camera_sessions')
def camera_sessions():
    """Get camera session history with recordings"""
    log_dir = Path(config['logging']['log_path'])
    if not log_dir.is_absolute():
        log_dir = BASE_DIR / log_dir
    
    recordings_dir = BASE_DIR / 'recordings'
    sessions = []
    
    # Read violations for each session
    violations_file = log_dir / "violations.json"
    violations_data = []
    if violations_file.exists():
        try:
            with open(violations_file, 'r', encoding='utf-8') as f:
                violations_data = json.load(f)
        except:
            pass
    
    # Group violations by date to create sessions
    session_dates = {}
    for v in violations_data:
        timestamp = v.get('timestamp', '')
        if timestamp:
            # Extract date from timestamp (format: YYYYMMDD_HHMMSS or YYYY-MM-DD...)
            if '_' in timestamp:
                date_part = timestamp.split('_')[0]
            else:
                date_part = timestamp[:10].replace('-', '')
            
            if date_part not in session_dates:
                session_dates[date_part] = {
                    'violations': [],
                    'start_time': timestamp,
                    'end_time': timestamp
                }
            session_dates[date_part]['violations'].append(v)
            session_dates[date_part]['end_time'] = timestamp
    
    # Check for video recordings
    if recordings_dir.exists():
        video_files = list(recordings_dir.glob('*.avi')) + list(recordings_dir.glob('*.mp4'))
        
        for video_file in sorted(video_files, key=lambda x: x.stat().st_mtime, reverse=True):
            mtime = video_file.stat().st_mtime
            file_date = datetime.fromtimestamp(mtime)
            date_key = file_date.strftime('%Y%m%d')
            
            # Count violations for this session (same date)
            session_violations = len(session_dates.get(date_key, {}).get('violations', []))
            
            sessions.append({
                'id': video_file.stem,
                'camera': 'Camera_1',
                'date': file_date.strftime('%Y-%m-%d'),
                'time': file_date.strftime('%H:%M:%S'),
                'status': 'Pasif',
                'violations': session_violations,
                'recording': video_file.name,
                'recording_path': f'/recordings/{video_file.name}'
            })
    
    # Add sessions from violations even if no recording
    for date_key in sorted(session_dates.keys(), reverse=True):
        # Check if this date already has a session
        date_formatted = f"{date_key[:4]}-{date_key[4:6]}-{date_key[6:8]}"
        if not any(s['date'] == date_formatted for s in sessions):
            violations = session_dates[date_key]['violations']
            first_time = session_dates[date_key]['start_time']
            if '_' in first_time:
                time_part = first_time.split('_')[1][:6]
                time_formatted = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
            else:
                time_formatted = first_time[11:19] if len(first_time) > 19 else '00:00:00'
            
            sessions.append({
                'id': f'session_{date_key}',
                'camera': 'Camera_1',
                'date': date_formatted,
                'time': time_formatted,
                'status': 'Pasif',
                'violations': len(violations),
                'recording': None,
                'recording_path': None
            })
    
    # Sort by date descending
    sessions.sort(key=lambda x: x['date'], reverse=True)
    
    # Add current active session if camera is running
    frame_path = BASE_DIR / 'logs' / 'current_frame.jpg'
    if frame_path.exists():
        mtime = frame_path.stat().st_mtime
        if time.time() - mtime <= 15:  # Active within 15 seconds
            # Count today's violations
            today = datetime.now().strftime('%Y%m%d')
            today_violations = len(session_dates.get(today, {}).get('violations', []))
            
            # Remove any existing entry for today
            sessions = [s for s in sessions if s.get('id') != 'current']
            
            sessions.insert(0, {
                'id': 'current',
                'camera': 'Camera_1',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': datetime.fromtimestamp(mtime).strftime('%H:%M:%S'),
                'status': 'Aktif',
                'violations': today_violations,
                'recording': None,
                'recording_path': None
            })
    
    return jsonify(sessions)

@app.route('/api/session/<session_id>/details')
def session_details(session_id):
    """Get detailed violations for a specific session with student breakdown"""
    log_dir = Path(config['logging']['log_path'])
    if not log_dir.is_absolute():
        log_dir = BASE_DIR / log_dir
    
    violations_file = log_dir / "violations.json"
    violations_data = []
    if violations_file.exists():
        try:
            with open(violations_file, 'r', encoding='utf-8') as f:
                violations_data = json.load(f)
        except:
            pass
    
    # Parse session date from session_id
    if session_id == 'current':
        target_date = datetime.now().strftime('%Y%m%d')
    elif session_id.startswith('session_'):
        target_date = session_id.replace('session_', '')
    else:
        # Try to extract date from recording filename
        target_date = session_id[:8] if len(session_id) >= 8 else datetime.now().strftime('%Y%m%d')
    
    # Filter violations for this session
    session_violations = []
    for v in violations_data:
        timestamp = v.get('timestamp', '')
        if '_' in timestamp:
            date_part = timestamp.split('_')[0]
        else:
            date_part = timestamp[:10].replace('-', '')
        
        if date_part == target_date:
            session_violations.append(v)
    
    # Group violations by "student" (in single camera, simulate multiple students based on face detection events)
    # For now, we'll create student groups based on violation timing clusters
    students = {}
    student_id = 1
    last_time = None
    current_student = f"Ogrenci {student_id}"
    
    violation_labels = {
        'FACE_DISAPPEARED': {'label': 'Yuz Algilanamadi', 'priority': 'Orta', 'icon': '👤'},
        'MULTIPLE_FACES': {'label': 'Birden Fazla Yuz', 'priority': 'Yuksek', 'icon': '👥'},
        'OBJECT_DETECTED': {'label': 'Yasak Nesne', 'priority': 'Yuksek', 'icon': '📱'},
        'MOUTH_MOVING': {'label': 'Agiz Hareketi', 'priority': 'Dusuk', 'icon': '👄'},
        'GAZE_AWAY': {'label': 'Goz Bakisi Kaydi', 'priority': 'Orta', 'icon': '👁️'},
        'EYE_TRACKING': {'label': 'Goz Takibi Uyarisi', 'priority': 'Orta', 'icon': '👁️'},
        'PHONE_DETECTED': {'label': 'Telefon Algilandi', 'priority': 'Yuksek', 'icon': '📱'},
        'BOOK_DETECTED': {'label': 'Kitap Algilandi', 'priority': 'Yuksek', 'icon': '📚'}
    }
    
    for v in sorted(session_violations, key=lambda x: x.get('timestamp', '')):
        timestamp = v.get('timestamp', '')
        v_type = v.get('type', 'UNKNOWN')
        
        # Parse time
        if '_' in timestamp:
            time_part = timestamp.split('_')[1][:6]
            time_formatted = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
        else:
            time_formatted = timestamp[11:19] if len(timestamp) > 19 else '00:00:00'
        
        # Get violation info
        v_info = violation_labels.get(v_type, {'label': v_type, 'priority': 'Bilinmiyor', 'icon': '⚠️'})
        
        # Initialize student if needed
        if current_student not in students:
            students[current_student] = {
                'id': student_id,
                'name': current_student,
                'violations': [],
                'total': 0,
                'high_priority': 0,
                'medium_priority': 0,
                'low_priority': 0
            }
        
        # Add violation
        students[current_student]['violations'].append({
            'type': v_info['label'],
            'icon': v_info['icon'],
            'time': time_formatted,
            'priority': v_info['priority'],
            'detail': v.get('details', f'{v_info["label"]} tespit edildi')
        })
        students[current_student]['total'] += 1
        
        if v_info['priority'] == 'Yuksek':
            students[current_student]['high_priority'] += 1
        elif v_info['priority'] == 'Orta':
            students[current_student]['medium_priority'] += 1
        else:
            students[current_student]['low_priority'] += 1
    
    # If no violations, create empty student
    if not students:
        students['Ogrenci 1'] = {
            'id': 1,
            'name': 'Ogrenci 1',
            'violations': [],
            'total': 0,
            'high_priority': 0,
            'medium_priority': 0,
            'low_priority': 0
        }
    
    return jsonify({
        'session_id': session_id,
        'date': f"{target_date[:4]}-{target_date[4:6]}-{target_date[6:8]}",
        'total_violations': len(session_violations),
        'students': list(students.values())
    })

@app.route('/recordings/<filename>')
def serve_recording(filename):
    """Serve video recording files"""
    from flask import send_from_directory
    recordings_dir = BASE_DIR / 'recordings'
    return send_from_directory(recordings_dir, filename)

@app.route('/api/screenshots')
def get_screenshots():
    """Get violation screenshots from output/violation_captures"""
    # Screenshots are saved in output_path/violation_captures by ViolationCapturer
    output_dir = Path(config['global']['output_path'])
    if not output_dir.is_absolute():
        output_dir = BASE_DIR / output_dir
    
    screenshots_dir = output_dir / 'violation_captures'
    screenshots = []
    
    if screenshots_dir.exists():
        # Get all image files
        image_files = list(screenshots_dir.glob('*.jpg')) + list(screenshots_dir.glob('*.png'))
        
        for img_file in sorted(image_files, key=lambda x: x.stat().st_mtime, reverse=True):
            mtime = img_file.stat().st_mtime
            file_date = datetime.fromtimestamp(mtime)
            file_size = img_file.stat().st_size
            
            # Parse violation type from filename (e.g., FACE_DISAPPEARED_20251205_100523.jpg)
            name_parts = img_file.stem.split('_')
            # Take the first parts before the date (YYYYMMDD format)
            violation_type = []
            for part in name_parts:
                if len(part) == 8 and part.isdigit():  # Date format check
                    break
                violation_type.append(part)
            violation_type = '_'.join(violation_type) if violation_type else img_file.stem
            
            # Translate violation types to Turkish
            violation_labels = {
                'FACE_DISAPPEARED': 'Yuz Algilanamadi',
                'MULTIPLE_FACES': 'Birden Fazla Yuz',
                'OBJECT_DETECTED': 'Yasak Nesne',
                'MOUTH_MOVING': 'Agiz Hareketi',
                'GAZE_AWAY': 'Goz Bakisi Kaydi',
                'EYE_TRACKING': 'Goz Takibi Uyarisi',
                'PHONE_DETECTED': 'Telefon Algilandi',
                'BOOK_DETECTED': 'Kitap Algilandi'
            }
            
            screenshots.append({
                'filename': img_file.name,
                'path': f'/screenshots/{img_file.name}',
                'date': file_date.strftime('%Y-%m-%d'),
                'time': file_date.strftime('%H:%M:%S'),
                'violation_type': violation_labels.get(violation_type, violation_type),
                'size': f'{file_size / 1024:.1f} KB'
            })
    
    return jsonify(screenshots)

@app.route('/screenshots/<filename>')
def serve_screenshot(filename):
    """Serve screenshot files from violation_captures"""
    from flask import send_from_directory
    output_dir = Path(config['global']['output_path'])
    if not output_dir.is_absolute():
        output_dir = BASE_DIR / output_dir
    screenshots_dir = output_dir / 'violation_captures'
    return send_from_directory(screenshots_dir, filename)

@app.route('/api/report/<session_id>')
def get_report_details(session_id):
    """Get detailed report for a specific session"""
    # Load violations data
    log_dir = Path(config['logging']['log_path'])
    if not log_dir.is_absolute():
        log_dir = BASE_DIR / log_dir
    violations_file = log_dir / 'violations.json'
    
    violations_data = []
    if violations_file.exists():
        try:
            with open(violations_file, 'r', encoding='utf-8') as f:
                violations_data = json.load(f)
        except:
            violations_data = []
    
    # Get screenshots
    output_dir = Path(config['global']['output_path'])
    if not output_dir.is_absolute():
        output_dir = BASE_DIR / output_dir
    screenshots_dir = output_dir / 'violation_captures'
    
    screenshots = []
    if screenshots_dir.exists():
        for img_file in sorted(screenshots_dir.glob('*.jpg'), key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
            mtime = img_file.stat().st_mtime
            screenshots.append({
                'filename': img_file.name,
                'path': f'/screenshots/{img_file.name}',
                'time': datetime.fromtimestamp(mtime).strftime('%H:%M:%S')
            })
    
    # Build violation breakdown
    violation_types = {
        'FACE_DISAPPEARED': {'count': 0, 'label': 'Yuz Algilanamadi', 'severity': 'Orta'},
        'MULTIPLE_FACES': {'count': 0, 'label': 'Birden Fazla Yuz', 'severity': 'Yuksek'},
        'OBJECT_DETECTED': {'count': 0, 'label': 'Yasak Nesne', 'severity': 'Yuksek'},
        'MOUTH_MOVING': {'count': 0, 'label': 'Agiz Hareketi', 'severity': 'Dusuk'},
        'GAZE_AWAY': {'count': 0, 'label': 'Goz Bakisi Kaydi', 'severity': 'Orta'},
        'EYE_TRACKING': {'count': 0, 'label': 'Goz Takibi Uyarisi', 'severity': 'Orta'},
        'PHONE_DETECTED': {'count': 0, 'label': 'Telefon Algilandi', 'severity': 'Yuksek'},
        'BOOK_DETECTED': {'count': 0, 'label': 'Kitap Algilandi', 'severity': 'Yuksek'}
    }
    
    timeline = []
    for v in violations_data:
        v_type = v.get('type', 'UNKNOWN')
        if v_type in violation_types:
            violation_types[v_type]['count'] += 1
        timeline.append({
            'time': v.get('timestamp', '')[:19].replace('T', ' '),
            'type': violation_types.get(v_type, {}).get('label', v_type),
            'severity': violation_types.get(v_type, {}).get('severity', 'Bilinmiyor')
        })
    
    total_violations = sum(vt['count'] for vt in violation_types.values())
    risk_score = min(100, total_violations * 10)
    risk_level = 'Yuksek' if risk_score > 60 else 'Orta' if risk_score > 30 else 'Dusuk'
    
    report = {
        'session_id': session_id,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'start_time': datetime.now().strftime('%H:%M:%S'),
        'duration': '45 dk',
        'camera': 'Camera_1',
        'total_violations': total_violations,
        'risk_score': risk_score,
        'risk_level': risk_level,
        'violation_breakdown': [
            {'type': vt['label'], 'count': vt['count'], 'severity': vt['severity']}
            for vt in violation_types.values() if vt['count'] > 0
        ],
        'timeline': timeline[-20:],  # Last 20 events
        'screenshots': screenshots
    }
    
    return jsonify(report)

@app.route('/api/report/<session_id>/pdf')
def download_report_pdf(session_id):
    """Generate and download PDF report"""
    from flask import Response
    
    # Get report data
    log_dir = Path(config['logging']['log_path'])
    if not log_dir.is_absolute():
        log_dir = BASE_DIR / log_dir
    violations_file = log_dir / 'violations.json'
    
    violations_data = []
    if violations_file.exists():
        try:
            with open(violations_file, 'r', encoding='utf-8') as f:
                violations_data = json.load(f)
        except:
            violations_data = []
    
    # Count violations by type
    violation_counts = {}
    for v in violations_data:
        v_type = v.get('type', 'UNKNOWN')
        violation_counts[v_type] = violation_counts.get(v_type, 0) + 1
    
    total_violations = len(violations_data)
    risk_score = min(100, total_violations * 10)
    risk_level = 'YUKSEK' if risk_score > 60 else 'ORTA' if risk_score > 30 else 'DUSUK'
    
    # Generate HTML for PDF
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Sinav Guvenlik Raporu - {session_id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
            h1 {{ color: #1e3a5f; border-bottom: 2px solid #1e3a5f; padding-bottom: 10px; }}
            h2 {{ color: #2563eb; margin-top: 30px; }}
            .header {{ display: flex; justify-content: space-between; margin-bottom: 30px; }}
            .info-box {{ background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 10px 0; }}
            .risk-high {{ color: #dc2626; font-weight: bold; }}
            .risk-medium {{ color: #f59e0b; font-weight: bold; }}
            .risk-low {{ color: #22c55e; font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background: #1e3a5f; color: white; }}
            tr:nth-child(even) {{ background: #f9fafb; }}
            .summary {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }}
            .summary-item {{ background: #f3f4f6; padding: 15px; border-radius: 8px; text-align: center; }}
            .summary-value {{ font-size: 24px; font-weight: bold; color: #1e3a5f; }}
            .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <h1>🛡️ Sinav Guvenlik Sistemi - Oturum Raporu</h1>
        
        <div class="info-box">
            <strong>Oturum ID:</strong> {session_id}<br>
            <strong>Tarih:</strong> {datetime.now().strftime('%Y-%m-%d')}<br>
            <strong>Saat:</strong> {datetime.now().strftime('%H:%M:%S')}<br>
            <strong>Kamera:</strong> Camera_1
        </div>
        
        <h2>Ozet Bilgiler</h2>
        <div class="summary">
            <div class="summary-item">
                <div class="summary-value">{total_violations}</div>
                <div>Toplam Ihlal</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{risk_score}%</div>
                <div>Risk Puani</div>
            </div>
            <div class="summary-item">
                <div class="summary-value {'risk-high' if risk_level == 'YUKSEK' else 'risk-medium' if risk_level == 'ORTA' else 'risk-low'}">{risk_level}</div>
                <div>Risk Seviyesi</div>
            </div>
        </div>
        
        <h2>Ihlal Dagilimi</h2>
        <table>
            <thead>
                <tr>
                    <th>Ihlal Turu</th>
                    <th>Sayi</th>
                    <th>Yuzde</th>
                </tr>
            </thead>
            <tbody>
    """
    
    violation_labels = {
        'FACE_DISAPPEARED': 'Yuz Algilanamadi',
        'MULTIPLE_FACES': 'Birden Fazla Yuz',
        'OBJECT_DETECTED': 'Yasak Nesne',
        'MOUTH_MOVING': 'Agiz Hareketi',
        'GAZE_AWAY': 'Goz Bakisi Kaydi',
        'EYE_TRACKING': 'Goz Takibi Uyarisi',
        'PHONE_DETECTED': 'Telefon Algilandi',
        'BOOK_DETECTED': 'Kitap Algilandi'
    }
    
    for v_type, count in violation_counts.items():
        label = violation_labels.get(v_type, v_type)
        percentage = (count / total_violations * 100) if total_violations > 0 else 0
        html_content += f"""
                <tr>
                    <td>{label}</td>
                    <td>{count}</td>
                    <td>{percentage:.1f}%</td>
                </tr>
        """
    
    if not violation_counts:
        html_content += """
                <tr>
                    <td colspan="3" style="text-align: center;">Ihlal tespit edilmedi</td>
                </tr>
        """
    
    html_content += f"""
            </tbody>
        </table>
        
        <h2>Ihlal Zaman Cizelgesi</h2>
        <table>
            <thead>
                <tr>
                    <th>Zaman</th>
                    <th>Ihlal Turu</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for v in violations_data[-15:]:  # Last 15 violations
        v_type = v.get('type', 'UNKNOWN')
        label = violation_labels.get(v_type, v_type)
        timestamp = v.get('timestamp', '')[:19].replace('T', ' ')
        html_content += f"""
                <tr>
                    <td>{timestamp}</td>
                    <td>{label}</td>
                </tr>
        """
    
    if not violations_data:
        html_content += """
                <tr>
                    <td colspan="2" style="text-align: center;">Zaman cizelgesi bos</td>
                </tr>
        """
    
    html_content += f"""
            </tbody>
        </table>
        
        <div class="footer">
            <p>Bu rapor Computer Vision ile Guvenli Sinav Denetim Sistemi tarafindan otomatik olarak olusturulmustur.</p>
            <p>Olusturulma Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """
    
    # Return HTML as downloadable file (browser can print to PDF)
    response = Response(html_content, mimetype='text/html')
    response.headers['Content-Disposition'] = f'attachment; filename=rapor_{session_id}_{datetime.now().strftime("%Y%m%d")}.html'
    return response

@app.route('/api/session/<session_id>/delete', methods=['DELETE'])
def delete_session(session_id):
    """Delete a session and its associated data"""
    try:
        # Get paths
        log_dir = Path(config['logging']['log_path'])
        if not log_dir.is_absolute():
            log_dir = BASE_DIR / log_dir
        
        recordings_dir = BASE_DIR / 'recordings'
        reports_dir = BASE_DIR / 'reports'
        
        # Parse session date from session_id
        if session_id.startswith('session_'):
            session_date = session_id.replace('session_', '')
        elif session_id == 'current':
            session_date = datetime.now().strftime('%Y%m%d')
        else:
            session_date = session_id[:8] if len(session_id) >= 8 else None
        
        deleted_items = []
        
        # Delete video recording if exists
        if recordings_dir.exists():
            for ext in ['*.avi', '*.mp4']:
                for video_file in recordings_dir.glob(ext):
                    if session_id in video_file.stem or (session_date and session_date in video_file.name):
                        video_file.unlink()
                        deleted_items.append(f"recording: {video_file.name}")
        
        # Delete violation captures for this session
        captures_dir = reports_dir / 'violation_captures'
        if captures_dir.exists() and session_date:
            for img_file in captures_dir.glob('*.jpg'):
                if session_date in img_file.name:
                    img_file.unlink()
                    deleted_items.append(f"capture: {img_file.name}")
        
        # Delete violations from violations.json
        violations_file = reports_dir / 'violations.json'
        if violations_file.exists() and session_date:
            try:
                with open(violations_file, 'r', encoding='utf-8') as f:
                    violations_data = json.load(f)
                
                # Filter out violations from this session
                original_count = len(violations_data)
                violations_data = [
                    v for v in violations_data 
                    if not (session_date in v.get('timestamp', ''))
                ]
                deleted_count = original_count - len(violations_data)
                
                # Save updated violations
                with open(violations_file, 'w', encoding='utf-8') as f:
                    json.dump(violations_data, f, indent=2, ensure_ascii=False)
                
                if deleted_count > 0:
                    deleted_items.append(f"violations: {deleted_count} records")
            except Exception as e:
                print(f"Error updating violations.json: {str(e)}")
        
        print(f"Deleted session {session_id}: {', '.join(deleted_items)}")
        return jsonify({
            'success': True, 
            'message': 'Session deleted successfully',
            'deleted': deleted_items
        })
        
    except Exception as e:
        print(f"Error deleting session: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)