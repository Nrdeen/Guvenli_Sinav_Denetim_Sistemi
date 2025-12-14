"""
Exam Proctoring System - Main Entry Point
نظام مراقبة الامتحانات

Run this file to start the system.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main_menu import show_menu

if __name__ == "__main__":
    try:
        show_menu()
    except KeyboardInterrupt:
        print("\n\n👋 System interrupted. Goodbye! - مع السلامة")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
