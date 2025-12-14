"""
Unified Launcher Server
This Flask server manages launching both exam systems:
1. Online System (Güvenli Sınav Denetim Sistemi) - Port 5000
2. Classroom System (EduView) - Port 3000
"""

from flask import Flask, render_template, jsonify, send_file
import subprocess
import sys
import os
from pathlib import Path
import threading
import time
import webbrowser

app = Flask(__name__, 
            template_folder='.',
            static_folder='.')

BASE_DIR = Path(__file__).resolve().parent

# Track running processes
processes = {
    'online': None,
    'classroom': None
}

@app.route('/')
def index():
    """Main launcher page"""
    return send_file('launcher_index.html')

@app.route('/launch/online', methods=['POST'])
def launch_online():
    """Launch Güvenli Sınav Denetim Sistemi (Flask - Port 5000)"""
    try:
        if processes['online'] is None or processes['online'].poll() is not None:
            # Start the online system
            online_script = BASE_DIR / 'start_system.py'
            
            if not online_script.exists():
                return jsonify({
                    'success': False,
                    'error': 'start_system.py not found'
                })
            
            # Start in new process
            processes['online'] = subprocess.Popen(
                [sys.executable, str(online_script)],
                cwd=str(BASE_DIR)
            )
            
            # Wait a moment for server to start
            time.sleep(2)
            
            return jsonify({
                'success': True,
                'url': 'http://localhost:5000',
                'message': 'Online system starting...'
            })
        else:
            return jsonify({
                'success': True,
                'url': 'http://localhost:5000',
                'message': 'Online system already running'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/launch/classroom', methods=['POST'])
def launch_classroom():
    """Launch EduView (Reflex - Port 3000)"""
    try:
        # Try multiple possible locations for EduView
        possible_paths = [
            BASE_DIR.parent / 'EduView-main',  # Most common from GitHub
            BASE_DIR.parent / 'EduView_main',
            BASE_DIR.parent / 'EduView',
            BASE_DIR.parent / 'eduview-main',
            BASE_DIR / 'EduView-main',
            BASE_DIR / 'EduView_main',
            BASE_DIR / 'EduView',
        ]
        
        eduview_path = None
        checked_paths = []
        for path in possible_paths:
            checked_paths.append(f"{path} - {'EXISTS' if path.exists() else 'NOT FOUND'}")
            if path.exists() and (path / 'rxconfig.py').exists():
                eduview_path = path
                print(f"✅ Found EduView at: {eduview_path}")
                break
        
        if not eduview_path:
            print("❌ EduView not found. Checked paths:")
            for cp in checked_paths:
                print(f"  - {cp}")
            
            return jsonify({
                'success': False,
                'error': 'EduView folder not found',
                'message': 'الرجاء تثبيت EduView أولاً',
                'debug_info': checked_paths,
                'instructions': {
                    'ar': [
                        '1. افتح PowerShell جديد',
                        f'2. cd "{BASE_DIR.parent}"',
                        '3. git clone https://github.com/Laoode/EduView.git EduView-main',
                        '4. cd EduView-main',
                        '5. python -m venv venv',
                        '6. venv\\Scripts\\activate',
                        '7. pip install -r requirements.txt',
                        '8. ارجع للصفحة واضغط مرة أخرى'
                    ],
                    'en': [
                        '1. Open new PowerShell',
                        f'2. cd "{BASE_DIR.parent}"',
                        '3. git clone https://github.com/Laoode/EduView.git EduView-main',
                        '4. cd EduView-main',
                        '5. python -m venv venv',
                        '6. venv\\Scripts\\activate',
                        '7. pip install -r requirements.txt',
                        '8. Return and click again'
                    ]
                }
            })
        
        if processes['classroom'] is None or processes['classroom'].poll() is not None:
            # Start EduView with Reflex
            processes['classroom'] = subprocess.Popen(
                ['reflex', 'run'],
                cwd=str(eduview_path),
                shell=True
            )
            
            # Wait for Reflex to start
            time.sleep(5)
            
            return jsonify({
                'success': True,
                'url': 'http://localhost:3000',
                'message': 'Classroom system starting...'
            })
        else:
            return jsonify({
                'success': True,
                'url': 'http://localhost:3000',
                'message': 'Classroom system already running'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/status')
def status():
    """Check status of both systems"""
    return jsonify({
        'online': {
            'running': processes['online'] is not None and processes['online'].poll() is None,
            'url': 'http://localhost:5000'
        },
        'classroom': {
            'running': processes['classroom'] is not None and processes['classroom'].poll() is None,
            'url': 'http://localhost:3000'
        }
    })

def open_browser():
    """Open browser after a short delay"""
    time.sleep(1)
    webbrowser.open('http://localhost:8080')

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  🎓 SINAV GÜVENLİK SİSTEMLERİ - Unified Launcher")
    print("="*70)
    print("\n  Launcher starting on: http://localhost:8080")
    print("\n  Available systems:")
    print("    • Online Sınav (Port 5000)")
    print("    • Sınıf İçi Sınav (Port 3000)")
    print("\n" + "="*70 + "\n")
    
    # Open browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run Flask app on port 8080 to avoid conflicts
    try:
        app.run(host='0.0.0.0', port=8080, debug=False)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down launcher...")
        if processes['online']:
            processes['online'].terminate()
        if processes['classroom']:
            processes['classroom'].terminate()
        print("✅ Launcher stopped.")
