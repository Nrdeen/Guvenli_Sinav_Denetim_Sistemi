"""
Test script to verify yolov8n.pt can detect people
"""
from ultralytics import YOLO
import cv2

# Load the model
print("Loading yolov8n.pt...")
model = YOLO("Güvenli Sınav Denetim Sistemi/models/yolov8n.pt")

# Print model info
print("\n=== Model Information ===")
print(f"Model classes: {model.names}")
print(f"Number of classes: {len(model.names)}")

# Test with webcam
print("\n=== Testing with webcam ===")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam")
    exit()

ret, frame = cap.read()
cap.release()

if not ret:
    print("Error: Could not read frame")
    exit()

print(f"Frame shape: {frame.shape}")

# Test with different confidence thresholds
thresholds = [0.1, 0.25, 0.3, 0.5]

for conf_thresh in thresholds:
    print(f"\n--- Testing with confidence threshold: {conf_thresh} ---")
    results = model(frame, conf=conf_thresh, iou=0.5, verbose=False)

    total_detections = 0
    for result in results:
        boxes = result.boxes
        total_detections = len(boxes)
        print(f"Total detections: {total_detections}")

        if total_detections > 0:
            for box in boxes:
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = model.names[cls]
                print(f"  - {class_name}: {conf:.3f}")

print("\n=== Test Complete ===")