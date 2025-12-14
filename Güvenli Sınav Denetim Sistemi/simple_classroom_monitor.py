"""
Simple Classroom Monitoring - Similar to the provided example
نظام مراقبة صف بسيط - مشابه للمثال المقدم

This is a simplified version that works like your example code.
Run this for simple student detection with names displayed.
"""

from ultralytics import YOLO
import cv2
from ultralytics.utils.plotting import Annotator
import os
import winsound
from src.detection.face_id import recognize_student


def simple_classroom_monitor_webcam():
    """
    Monitor classroom using webcam (like cheating_detect0 in your example)
    Shows student names in green boxes
    """
    print("\n🎥 Simple Classroom Monitoring - Webcam")
    print("=" * 60)
    print("Starting webcam monitoring...")
    print("Press 'q' to quit")
    print("=" * 60)
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)
    
    if not cap.isOpened():
        print("❌ Cannot open webcam!")
        return
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to grab frame")
            break
        
        frame_count += 1
        
        # Process every 5th frame for better performance
        if frame_count % 5 != 0:
            cv2.imshow('Classroom Monitoring', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue
        
        # Recognize students using face recognition
        recognized = recognize_student(frame)
        
        # Draw boxes and names for each detected student
        for sid, name, (top, right, bottom, left), confidence in recognized:
            # Determine color based on recognition
            if sid == "unknown":
                color = (0, 0, 255)  # Red for unknown person
                label = "Unknown"
            else:
                color = (0, 255, 0)  # Green for recognized student
                label = name  # Display student's name
            
            # Draw bounding box
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Draw label with name
            cv2.putText(
                frame,
                label,
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )
        
        # Display the frame
        cv2.imshow('Classroom Monitoring', frame)
        
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("\n✅ Monitoring stopped")


def simple_classroom_monitor_video(video_path=None):
    """
    Monitor classroom using video file
    Shows student names in green boxes
    """
    if not video_path:
        print("Please provide a video path")
        return
    
    print(f"\n🎥 Simple Classroom Monitoring - Video: {video_path}")
    print("=" * 60)
    print("Press 'q' to quit")
    print("=" * 60)
    
    # Open video file
    cap = cv2.VideoCapture(video_path)
    cap.set(3, 640)
    cap.set(4, 480)
    
    if not cap.isOpened():
        print(f"❌ Cannot open video: {video_path}")
        return
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("End of video")
            break
        
        frame_count += 1
        
        # Process every 5th frame
        if frame_count % 5 != 0:
            cv2.imshow('Classroom Monitoring - Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue
        
        # Recognize students
        recognized = recognize_student(frame)
        
        # Draw boxes and names
        for sid, name, (top, right, bottom, left), confidence in recognized:
            if sid == "unknown":
                color = (0, 0, 255)  # Red
                label = "Unknown"
            else:
                color = (0, 255, 0)  # Green
                label = name
            
            # Draw rectangle
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Draw name
            cv2.putText(
                frame,
                label,
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2
            )
        
        # Display
        cv2.imshow('Classroom Monitoring - Video', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("\n✅ Video monitoring stopped")


def simple_classroom_monitor_rtsp(rtsp_url):
    """
    Monitor classroom using RTSP camera
    Shows student names in green boxes
    
    Args:
        rtsp_url: RTSP URL of the camera (e.g., "rtsp://192.168.1.20/live")
    """
    print(f"\n🎥 Simple Classroom Monitoring - RTSP Camera")
    print(f"URL: {rtsp_url}")
    print("=" * 60)
    print("Press 'q' to quit")
    print("=" * 60)
    
    # Open RTSP stream
    cap = cv2.VideoCapture(rtsp_url)
    
    if not cap.isOpened():
        print(f"❌ Cannot connect to RTSP camera: {rtsp_url}")
        return
    
    print("✅ Connected to camera")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("⚠️  Connection lost")
            break
        
        frame_count += 1
        
        # Process every 5th frame
        if frame_count % 5 != 0:
            cv2.imshow('Classroom Monitoring - RTSP', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue
        
        # Recognize students
        recognized = recognize_student(frame)
        
        # Draw boxes and names
        for sid, name, (top, right, bottom, left), confidence in recognized:
            if sid == "unknown":
                color = (0, 0, 255)  # Red
                label = "Unknown"
            else:
                color = (0, 255, 0)  # Green
                label = name
            
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Display
        cv2.imshow('Classroom Monitoring - RTSP', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("\n✅ RTSP monitoring stopped")


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("    SIMPLE CLASSROOM MONITORING")
    print("    مراقبة الصف البسيطة")
    print("=" * 60)
    print()
    print("Select source:")
    print("1) Webcam")
    print("2) Video File")
    print("3) RTSP Camera")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        simple_classroom_monitor_webcam()
    elif choice == "2":
        video_path = input("Enter video file path: ").strip()
        simple_classroom_monitor_video(video_path)
    elif choice == "3":
        rtsp_url = input("Enter RTSP URL (e.g., rtsp://192.168.1.20/live): ").strip()
        simple_classroom_monitor_rtsp(rtsp_url)
    else:
        print("Invalid choice!")
