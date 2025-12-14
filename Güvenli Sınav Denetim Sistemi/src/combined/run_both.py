"""
Combined Monitoring Mode
Run both classroom and online monitoring simultaneously
"""

import threading
import logging
from src.classroom_monitor.rtsp_reader import start_classroom_monitoring
from src.online_agent.agent import start_online_monitoring

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start_combined_monitoring():
    """
    Start both classroom and online monitoring in parallel
    """
    print("\n🔄 Combined Monitoring Mode")
    print("=" * 60)
    print("This mode will run:")
    print("  1. Classroom monitoring (RTSP cameras)")
    print("  2. Online monitoring (Student webcam)")
    print()
    print("Both systems will run in parallel.")
    print("=" * 60)
    print()
    
    choice = input("Continue? (y/n): ").strip().lower()
    
    if choice != 'y':
        print("\n❌ Cancelled. Returning to menu...")
        input("Press Enter to continue...")
        return
    
    logger.info("🔄 Starting combined monitoring mode...")
    
    # Create threads for each monitoring mode
    classroom_thread = threading.Thread(
        target=start_classroom_monitoring,
        name="ClassroomMonitor",
        daemon=True
    )
    
    online_thread = threading.Thread(
        target=start_online_monitoring,
        name="OnlineMonitor",
        daemon=True
    )
    
    # Start both threads
    print("\n🚀 Starting classroom monitoring...")
    classroom_thread.start()
    
    print("🚀 Starting online monitoring...")
    online_thread.start()
    
    print("\n✅ Both monitoring systems are running")
    print("Press Ctrl+C to stop all monitoring")
    print()
    
    try:
        # Wait for both threads
        classroom_thread.join()
        online_thread.join()
    except KeyboardInterrupt:
        logger.info("⚠️  Combined monitoring interrupted by user")
        print("\n\n⚠️  Stopping all monitoring systems...")
    
    logger.info("✅ Combined monitoring stopped")
    print("\n✅ All monitoring systems stopped")
    input("Press Enter to return to menu...")


if __name__ == "__main__":
    start_combined_monitoring()
