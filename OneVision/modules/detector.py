import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple
import time

class ObjectDetector:
    """YOLO-based object detection with spatial analysis"""
    
    def __init__(self, model_path: str = "yolov8n.pt", confidence: float = 0.5):
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.class_names = self.model.names
        self.last_detection_time = 0
        
    def detect_objects(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect objects in frame and return structured data
        Returns list of detected objects with spatial information
        """
        results = self.model(frame, conf=self.confidence, verbose=False)
        detections = []
        
        if results and len(results) > 0:
            boxes = results[0].boxes
            if boxes is not None:
                for box in boxes:
                    # Extract box coordinates and confidence
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    # Calculate spatial properties
                    center_x = (x1 + x2) / 2
                    center_y = (y1 + y2) / 2
                    width = x2 - x1
                    height = y2 - y1
                    area = width * height
                    
                    # Determine spatial position
                    frame_width = frame.shape[1]
                    frame_height = frame.shape[0]
                    
                    # Horizontal position
                    if center_x < frame_width * 0.33:
                        h_position = "left"
                    elif center_x > frame_width * 0.67:
                        h_position = "right"
                    else:
                        h_position = "center"
                    
                    # Vertical position
                    if center_y < frame_height * 0.33:
                        v_position = "top"
                    elif center_y > frame_height * 0.67:
                        v_position = "bottom"
                    else:
                        v_position = "middle"
                    
                    # Distance estimation (rough approximation based on object size)
                    relative_size = area / (frame_width * frame_height)
                    if relative_size > 0.3:
                        distance = "very close"
                    elif relative_size > 0.1:
                        distance = "close"
                    elif relative_size > 0.02:
                        distance = "medium distance"
                    else:
                        distance = "far"
                    
                    detection = {
                        'class_name': self.class_names[class_id],
                        'confidence': float(confidence),
                        'bbox': [float(x1), float(y1), float(x2), float(y2)],
                        'center': [float(center_x), float(center_y)],
                        'size': [float(width), float(height)],
                        'area': float(area),
                        'position': f"{v_position} {h_position}",
                        'distance': distance,
                        'relative_size': float(relative_size)
                    }
                    
                    detections.append(detection)
        
        # Sort by area (larger objects first)
        detections.sort(key=lambda x: x['area'], reverse=True)
        self.last_detection_time = time.time()
        
        return detections
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """Draw bounding boxes and labels on frame"""
        annotated_frame = frame.copy()
        
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            class_name = detection['class_name']
            confidence = detection['confidence']
            position = detection['position']
            distance = detection['distance']
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            
            # Create label
            label = f"{class_name} ({confidence:.2f})"
            spatial_info = f"{position}, {distance}"
            
            # Draw labels
            cv2.putText(annotated_frame, label, (int(x1), int(y1) - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(annotated_frame, spatial_info, (int(x1), int(y2) + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        return annotated_frame