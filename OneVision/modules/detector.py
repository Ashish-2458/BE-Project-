import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict
import time

# High-priority objects for navigation
DANGER_CLASSES = {"person", "car", "truck", "bus", "motorcycle", "bicycle"}
OBSTACLE_CLASSES = {"chair", "couch", "bed", "dining table", "toilet", "potted plant",
                    "suitcase", "backpack", "umbrella", "handbag", "bottle", "cup"}

class ObjectDetector:
    """YOLO-based object detection with spatial analysis"""

    def __init__(self, model_path: str = "yolov8n.pt", confidence: float = 0.5):
        self.model = YOLO(model_path)
        self.confidence = confidence
        self.class_names = self.model.names
        self.last_detection_time = 0

    def detect_objects(self, frame: np.ndarray) -> List[Dict]:
        results = self.model(frame, conf=self.confidence, verbose=False)
        detections = []

        if results and len(results) > 0:
            boxes = results[0].boxes
            if boxes is not None:
                fw, fh = frame.shape[1], frame.shape[0]
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf  = float(box.conf[0].cpu().numpy())
                    cid   = int(box.cls[0].cpu().numpy())
                    name  = self.class_names[cid]

                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    area = (x2 - x1) * (y2 - y1)

                    h_pos = "left" if cx < fw * 0.33 else ("right" if cx > fw * 0.67 else "center")
                    v_pos = "top"  if cy < fh * 0.33 else ("bottom" if cy > fh * 0.67 else "middle")

                    rel = area / (fw * fh)
                    size_dist = ("very close" if rel > 0.3 else
                                 "close"      if rel > 0.1 else
                                 "medium"     if rel > 0.02 else "far")

                    is_danger   = name in DANGER_CLASSES
                    is_obstacle = name in OBSTACLE_CLASSES

                    detections.append({
                        "class_name":    name,
                        "confidence":    conf,
                        "bbox":          [float(x1), float(y1), float(x2), float(y2)],
                        "center":        [float(cx), float(cy)],
                        "area":          float(area),
                        "position":      f"{v_pos} {h_pos}",
                        "distance":      size_dist,
                        "distance_meters": None,   # filled by depth module
                        "is_danger":     is_danger,
                        "is_obstacle":   is_obstacle,
                        "relative_size": float(rel),
                    })

        detections.sort(key=lambda x: x["area"], reverse=True)
        self.last_detection_time = time.time()
        return detections

    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        out = frame.copy()
        for det in detections:
            x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
            dm   = det.get("distance_meters")
            name = det["class_name"]

            # Color by danger zone
            if dm is not None:
                if   dm < 1.5: color = (0, 0, 255)    # RED  - immediate
                elif dm < 3.0: color = (0, 100, 255)   # ORANGE - close
                elif dm < 6.0: color = (0, 220, 255)   # YELLOW - medium
                else:          color = (0, 255, 80)    # GREEN - far
            elif det["is_danger"]:
                color = (0, 80, 255)
            else:
                color = (0, 255, 80)

            dist_lbl = f"{dm}m" if dm else det["distance"]
            label    = f"{name} {dist_lbl}"

            # Box
            thick = 3 if det["is_danger"] else 2
            cv2.rectangle(out, (x1, y1), (x2, y2), color, thick)

            # Label background
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 1)
            cv2.rectangle(out, (x1, y1 - th - 8), (x1 + tw + 6, y1), color, -1)
            cv2.putText(out, label, (x1 + 3, y1 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 0, 0), 1)

            # Position tag below box
            cv2.putText(out, det["position"], (x1, y2 + 16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1)

        return out
