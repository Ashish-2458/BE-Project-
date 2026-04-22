"""
Depth estimation module for distance calculation
Simplified version optimized for speed
"""
import cv2
import numpy as np
import torch
from transformers import pipeline

class DepthEstimator:
    def __init__(self):
        self.pipe = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.enabled = False
        
    def initialize(self):
        """Initialize depth estimation model"""
        try:
            print(f"Loading Depth Anything V2 model on {self.device}...")
            # Use small model for speed
            self.pipe = pipeline(
                task="depth-estimation",
                model="LiheYoung/depth-anything-small-hf",
                device=0 if self.device == "cuda" else -1
            )
            print("✅ Depth estimation model loaded")
            self.enabled = True
            return True
        except Exception as e:
            print(f"⚠️  Depth model failed, using fallback: {e}")
            self.enabled = False
            return False
    
    def estimate_depth(self, frame):
        """Estimate depth for entire frame"""
        if not self.enabled or self.pipe is None:
            return self._simple_depth(frame)
            
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            from PIL import Image
            pil_image = Image.fromarray(rgb_frame)
            
            # Get depth
            result = self.pipe(pil_image)
            depth_map = np.array(result["depth"])
            
            # Normalize
            depth_map = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)
            return depth_map.astype(np.uint8)
            
        except Exception as e:
            return self._simple_depth(frame)
    
    def _simple_depth(self, frame):
        """Simple fallback depth estimation"""
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Use gradient for depth approximation
        grad_x = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
        gradient = np.sqrt(grad_x**2 + grad_y**2)
        
        depth = cv2.normalize(gradient, None, 0, 255, cv2.NORM_MINMAX)
        return 255 - depth.astype(np.uint8)
    
    def get_distance(self, depth_map, bbox):
        """
        Get distance for object from depth map
        Args:
            depth_map: Depth map array
            bbox: [x1, y1, x2, y2] bounding box
        Returns: Distance in meters (float)
        """
        if depth_map is None:
            return None
            
        try:
            x1, y1, x2, y2 = [int(v) for v in bbox]
            h, w = depth_map.shape
            
            # Clamp coordinates
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            # Get median depth in bbox region
            region = depth_map[y1:y2, x1:x2]
            if region.size > 0:
                depth_value = np.median(region)
            else:
                return None
            
            # Convert to meters (inverse relationship)
            normalized = (255 - depth_value) / 255.0
            distance = 0.5 + (normalized * 9.5)  # 0.5m to 10m range
            
            return round(distance, 1)
            
        except Exception as e:
            return None
