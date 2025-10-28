"""
Camera handling for capturing images
"""
import cv2
import numpy as np
import base64
from typing import Optional, Tuple
import config

class CameraHandler:
    """Handles camera operations for image capture"""
    
    def __init__(self, camera_index: int = config.CAMERA_INDEX):
        self.camera_index = camera_index
        self.cap = None
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize camera connection"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                print(f"❌ Failed to open camera {self.camera_index}")
                return False
                
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
            
            # Test capture
            ret, frame = self.cap.read()
            if not ret or frame is None:
                print("❌ Failed to capture test frame")
                return False
                
            self.is_initialized = True
            print("✅ Camera initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Camera initialization error: {e}")
            return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a single frame from camera"""
        if not self.is_initialized or self.cap is None:
            print("❌ Camera not initialized")
            return None
            
        try:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                return frame
            else:
                print("❌ Failed to capture frame")
                return None
                
        except Exception as e:
            print(f"❌ Frame capture error: {e}")
            return None
    
    def frame_to_base64(self, frame: np.ndarray) -> Optional[str]:
        """Convert frame to base64 string for API upload"""
        try:
            # Resize if too large
            height, width = frame.shape[:2]
            max_width, max_height = config.MAX_IMAGE_SIZE
            
            if width > max_width or height > max_height:
                scale = min(max_width/width, max_height/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                frame = cv2.resize(frame, (new_width, new_height))
            
            # Encode as JPEG
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), config.IMAGE_QUALITY]
            _, buffer = cv2.imencode('.jpg', frame, encode_param)
            
            # Convert to base64
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            return image_base64
            
        except Exception as e:
            print(f"❌ Base64 encoding error: {e}")
            return None
    
    def capture_and_encode(self) -> Optional[str]:
        """Capture frame and return as base64 string"""
        frame = self.capture_frame()
        if frame is not None:
            return self.frame_to_base64(frame)
        return None
    
    def release(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.is_initialized = False
            print("📷 Camera released")
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.release()