import reflex as rx

class ThresholdState(rx.State):
    # Default values optimized for Model 1 - balanced for accuracy
    confidence_threshold: float = 0.30  # Balanced threshold for Model 1
    iou_threshold: float = 0.50  # Balanced IOU threshold
    duration_threshold: float = 5.0
    
    # Minimum thresholds to prevent too many false detections
    MIN_CONFIDENCE_THRESHOLD: float = 0.15  # Minimum 15% confidence
    MIN_IOU_THRESHOLD: float = 0.20  # Minimum 20% IOU

    def increment_confidence(self):
        if self.confidence_threshold < 1.0:
            self.confidence_threshold += 0.01
            self.confidence_threshold = round(self.confidence_threshold, 2)

    def decrement_confidence(self):
        if self.confidence_threshold > self.MIN_CONFIDENCE_THRESHOLD:
            self.confidence_threshold -= 0.01
            self.confidence_threshold = round(self.confidence_threshold, 2)
            # Ensure it doesn't go below minimum
            if self.confidence_threshold < self.MIN_CONFIDENCE_THRESHOLD:
                self.confidence_threshold = self.MIN_CONFIDENCE_THRESHOLD

    def increment_second_threshold(self, active_model: int):
        if active_model == 3:
            if self.duration_threshold < 10.0: 
                self.duration_threshold += 0.1
                self.duration_threshold = round(self.duration_threshold, 1)
        else:
            if self.iou_threshold < 1.0:
                self.iou_threshold += 0.01
                self.iou_threshold = round(self.iou_threshold, 2)

    def decrement_second_threshold(self, active_model: int):
        if active_model == 3:
            if self.duration_threshold > 1.0: 
                self.duration_threshold -= 0.1
                self.duration_threshold = round(self.duration_threshold, 1)
        else:
            if self.iou_threshold > self.MIN_IOU_THRESHOLD:
                self.iou_threshold -= 0.01
                self.iou_threshold = round(self.iou_threshold, 2)
                # Ensure it doesn't go below minimum
                if self.iou_threshold < self.MIN_IOU_THRESHOLD:
                    self.iou_threshold = self.MIN_IOU_THRESHOLD

    def set_confidence_from_str(self, value: str):
        try:
            new_value = float(value)
            # Enforce minimum threshold
            if new_value < self.MIN_CONFIDENCE_THRESHOLD:
                self.confidence_threshold = self.MIN_CONFIDENCE_THRESHOLD
                print(f"[WARNING] Confidence threshold too low. Set to minimum: {self.MIN_CONFIDENCE_THRESHOLD}")
            else:
                self.confidence_threshold = new_value
        except ValueError:
            print("Invalid input for confidence threshold")

    def set_second_threshold_from_str(self, value: str, active_model: int):
        try:
            new_value = float(value)
            if active_model == 3:
                self.duration_threshold = new_value
            else:
                # Enforce minimum IOU threshold
                if new_value < self.MIN_IOU_THRESHOLD:
                    self.iou_threshold = self.MIN_IOU_THRESHOLD
                    print(f"[WARNING] IOU threshold too low. Set to minimum: {self.MIN_IOU_THRESHOLD}")
                else:
                    self.iou_threshold = new_value
        except ValueError:
            print("Invalid input for second threshold")

    def set_model_defaults(self, model_number: int):
        """Set default threshold values based on model number"""
        if model_number == 3:  
            self.confidence_threshold = 0.6
            self.duration_threshold = 5.0
        elif model_number == 1:  # Model 1 - Classroom behavior detection
            self.confidence_threshold = 0.30  # Balanced threshold for accuracy
            self.iou_threshold = 0.50  # Balanced IOU threshold
        elif model_number == 2:  # Model 2 - Cheating detection
            self.confidence_threshold = 0.25
            self.iou_threshold = 0.70
        else:  # Default YOLO models
            self.confidence_threshold = 0.25
            self.iou_threshold = 0.70