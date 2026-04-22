"""
Depth estimation using Depth Anything V2
"""
import cv2
import numpy as np
import torch
from transformers import pipeline
from config import DEPTH_MODEL_NAME

class DepthEstimator:
    def __init__(self):
        self.pipe = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def initialize(self):
        """Initialize depth estimation model"""
        try:
            print(f"Loading Depth Anything V2 model on {self.device}...")
            # Try different model names for Depth Anything V2
            model_options = [
                "LiheYoung/depth-anything-small-hf",
                "depth-anything/Depth-Anything-V2-Small-hf", 
                "Intel/dpt-large",
                "Intel/dpt-hybrid-midas"
            ]
            
            for model_name in model_options:
                try:
                    print(f"Trying model: {model_name}")
                    self.pipe = pipeline(
                        task="depth-estimation",
                        model=model_name,
                        device=0 if self.device == "cuda" else -1
                    )
                    print(f"Depth estimation model loaded successfully: {model_name}")
                    return True
                except Exception as model_error:
                    print(f"Failed to load {model_name}: {model_error}")
                    continue
            
            print("All depth models failed, falling back to simple depth estimation")
            return False
            
        except Exception as e:
            print(f"Error loading depth model: {e}")
            return False
    
    def estimate_depth(self, frame):
        """
        Estimate depth for entire frame
        Returns: depth map as numpy array
        """
        if self.pipe is None:
            # Fallback to simple depth estimation
            return self._simple_depth_estimation(frame)
            
        try:
            # Convert BGR to RGB and then to PIL Image
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            from PIL import Image
            pil_image = Image.fromarray(rgb_frame)
            
            # Get depth estimation
            result = self.pipe(pil_image)
            depth_map = np.array(result["depth"])
            
            # Normalize depth map
            depth_map = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)
            depth_map = depth_map.astype(np.uint8)
            
            return depth_map
            
        except Exception as e:
            print(f"Error in depth estimation: {e}")
            return self._simple_depth_estimation(frame)
    
    def _simple_depth_estimation(self, frame):
        """
        Simple depth estimation fallback using image processing
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Calculate gradient magnitude (edges often indicate depth changes)
            grad_x = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Normalize gradient
            gradient_norm = cv2.normalize(gradient_magnitude, None, 0, 255, cv2.NORM_MINMAX)
            
            # Invert so that edges (likely closer objects) appear brighter
            depth_estimate = 255 - gradient_norm.astype(np.uint8)
            
            # Apply some smoothing
            depth_estimate = cv2.medianBlur(depth_estimate, 5)
            
            return depth_estimate
            
        except Exception as e:
            print(f"Error in simple depth estimation: {e}")
            # Return a basic depth map based on vertical position
            h, w = frame.shape[:2]
            depth_map = np.zeros((h, w), dtype=np.uint8)
            for i in range(h):
                # Objects lower in frame are typically closer
                depth_value = int(255 * (h - i) / h)
                depth_map[i, :] = depth_value
            return depth_map
    
    def get_object_distance(self, depth_map, center_point, bbox=None):
        """
        Get distance for specific object
        Args:
            depth_map: Depth map from estimate_depth
            center_point: [x, y] center of object
            bbox: Optional [x1,y1,x2,y2] for region-based estimation
        Returns: Estimated distance in meters
        """
        if depth_map is None:
            return None
            
        try:
            h, w = depth_map.shape
            x, y = center_point
            
            # Ensure coordinates are within bounds
            x = max(0, min(w-1, x))
            y = max(0, min(h-1, y))
            
            if bbox is not None:
                # Use region-based estimation for better accuracy
                x1, y1, x2, y2 = bbox
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                
                # Get median depth in bounding box region
                region = depth_map[y1:y2, x1:x2]
                if region.size > 0:
                    depth_value = np.median(region)
                else:
                    depth_value = depth_map[y, x]
            else:
                # Use center point depth
                depth_value = depth_map[y, x]
            
            # Convert normalized depth to approximate meters
            # This is a rough approximation - would need calibration for accuracy
            distance_meters = self._depth_to_meters(depth_value)
            
            return distance_meters
            
        except Exception as e:
            print(f"Error calculating object distance: {e}")
            return None
    
    def _depth_to_meters(self, depth_value):
        """
        Convert normalized depth value to approximate meters
        This is a rough approximation based on typical indoor scenes
        """
        # Inverse relationship: higher depth values = closer objects
        # Normalize from 0-255 to 0-1, then invert
        normalized = (255 - depth_value) / 255.0
        
        # Map to reasonable distance range (0.5m to 10m)
        min_distance = 0.5
        max_distance = 10.0
        
        distance = min_distance + (normalized * (max_distance - min_distance))
        return round(distance, 1)
    
    def visualize_depth(self, depth_map):
        """Create colorized depth visualization"""
        if depth_map is None:
            return None
            
        # Apply colormap for better visualization
        depth_colored = cv2.applyColorMap(depth_map, cv2.COLORMAP_JET)
        return depth_colored