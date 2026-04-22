"""
YOLO object detection system
"""
import cv2
import numpy as np
from ultralytics import YOLO
from config import YOLO_MODEL_PATH, CONFIDENCE_THRESHOLD, NMS_THRESHOLD, PRIORITY_OBJECTS

class YOLODetector:
    def __init__(self):
        self.model = None
        self.class_names = []
        
    def initialize(self):
        """Initialize YOLO model"""
        try:
            print("Loading YOLO model...")
            self.model = YOLO(YOLO_MODEL_PATH)
            self.class_names = self.model.names
            print(f"YOLO model loaded with {len(self.class_names)} classes")
            return True
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            return False
    
    def detect_objects(self, frame):
        """
        Detect objects in frame
        Returns: List of detections with format:
        [{'class': str, 'confidence': float, 'bbox': [x1,y1,x2,y2], 'center': [x,y]}]
        """
        if self.model is None:
            return []
            
        try:
            results = self.model(frame, conf=CONFIDENCE_THRESHOLD, iou=NMS_THRESHOLD)
            detections = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        class_name = self.class_names[class_id]
                        
                        # Calculate center point
                        center_x = int((x1 + x2) / 2)
                        center_y = int((y1 + y2) / 2)
                        
                        detection = {
                            'class': class_name,
                            'confidence': float(confidence),
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'center': [center_x, center_y],
                            'priority': class_name in PRIORITY_OBJECTS
                        }
                        
                        detections.append(detection)
            
            return detections
            
        except Exception as e:
            print(f"Error in object detection: {e}")
            return []
    
    def draw_detections(self, frame, detections):
        """Draw detection boxes and labels on frame"""
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            class_name = detection['class']
            confidence = detection['confidence']
            
            # Color based on priority
            color = (0, 255, 0) if detection['priority'] else (255, 0, 0)
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            cv2.putText(frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw center point
            center_x, center_y = detection['center']
            cv2.circle(frame, (center_x, center_y), 3, color, -1)
        
        return frame