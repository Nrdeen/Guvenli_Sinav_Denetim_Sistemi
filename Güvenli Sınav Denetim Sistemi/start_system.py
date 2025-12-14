#!/usr/bin/env python3
"""
Exam Security System Launcher
Launches both the camera monitoring system and web dashboard simultaneously
"""

import subprocess
import sys
import time
import threading
import os
from pathlib import Path

# Shutdown flag file
SHUTDOWN_FLAG_FILE = Path(__file__).parent / '.shutdown_flag'

def cleanup_shutdown_flag():
    """Remove shutdown flag if exists"""
    if SHUTDOWN_FLAG_FILE.exists():
        SHUTDOWN_FLAG_FILE.unlink()

def check_shutdown_flag(dashboard_process, main_process_pid):
    """Monitor shutdown flag file"""
    while True:
        if SHUTDOWN_FLAG_FILE.exists():
            print("\n\n[!] Shutdown signal received from dashboard...")
            cleanup_shutdown_flag()
            
            # Terminate dashboard
            try:
                dashboard_process.terminate()
                dashboard_process.wait(timeout=2)
            except:
                dashboard_process.kill()
            
            # Terminate main camera process
            if main_process_pid:
                try:
                    if sys.platform == 'win32':
                        subprocess.run(['taskkill', '/F', '/PID', str(main_process_pid)], 
                                      capture_output=True)
                    else:
                        os.kill(main_process_pid, 9)
                except:
                    pass
            
            print("[✓] System shutdown complete.\n")
            os._exit(0)
        
        time.sleep(0.5)

def main():
    print("=" * 60)
    print("  SINAV GUVENLIK SISTEMI - Baslatiliyor...")
    print("=" * 60)
    
    base_dir = Path(__file__).parent
    
    # Clean up any existing shutdown flag
    cleanup_shutdown_flag()
    
    # Start Flask dashboard in background
    print("\n[1/2] Dashboard Sunucusu Baslatiliyor...")
    dashboard_process = subprocess.Popen(
        [sys.executable, str(base_dir / "src" / "dashboard" / "app.py")],
        cwd=str(base_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give Flask time to start
    time.sleep(2)
    
    print("       Dashboard http://127.0.0.1:5000 adresinde calisiyor")
    print("\n[2/2] Kamera Izleme Sistemi Baslatiliyor...")
    print("       Kamera penceresi acilacak...")
    print("\n" + "=" * 60)
    print("  SISTEM HAZIR")
    print("=" * 60)
    print("\n  Kamera Izleme: Aktif")
    print("   Dashboard: http://127.0.0.1:5000")
    print("\n  Kamera penceresinde 'q' tusuna basarak izlemeyi durdurun")
    print("  Dashboard'da 'Sistemi Kapat' ile tum sistemi kapatabilirsiniz")
    print("  Ctrl+C ile tum sistemi durdurabilirsiniz")
    print("=" * 60 + "\n")
    
    main_process = None
    
    try:
        # Start main camera system
        main_process = subprocess.Popen(
            [sys.executable, str(base_dir / "src" / "main.py")],
            cwd=str(base_dir)
        )
        
        # Start shutdown flag monitor thread
        monitor_thread = threading.Thread(
            target=check_shutdown_flag, 
            args=(dashboard_process, main_process.pid),
            daemon=True
        )
        monitor_thread.start()
        
        # Wait for camera process to finish (when 'q' is pressed)
        main_process.wait()
        
        print("\n\n[!] Kamera izleme durduruldu, sistem kapatiliyor...")
        
    except KeyboardInterrupt:
        print("\n\n[!] Sistem kapatiliyor...")
    finally:
        # Cleanup
        cleanup_shutdown_flag()
        
        if dashboard_process:
            dashboard_process.terminate()
            try:
                dashboard_process.wait(timeout=3)
            except:
                dashboard_process.kill()
        
        if main_process and main_process.poll() is None:
            main_process.terminate()
            try:
                main_process.wait(timeout=3)
            except:
                main_process.kill()
        
        print("[✓] Dashboard durduruldu")
        print("[✓] Kamera izleme durduruldu")
        print("\nSistem kapatma tamamlandi.\n")

if __name__ == "__main__":
    main()
