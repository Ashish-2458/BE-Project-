import cv2
import threading
import time
from typing import Optional, Tuple
import numpy as np

class CameraCapture:
    """Handles webcam capture with threading for smooth performance"""
    
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        self.frame = None
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        
    def start(self) -> bool:
        """Initialize and start camera capture"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                print(f"Error: Could not open camera {self.camera_index}")
                return False
                
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.running = True
            self.thread = threading.Thread(target=self._capture_loop)
            self.thread.daemon = True
            self.thread.start()
            
            print(f"Camera started successfully at {self.width}x{self.height}")
            return True
            
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False
    
    def _capture_loop(self):
        """Continuous frame capture in separate thread"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame.copy()
            time.sleep(0.01)  # Small delay to prevent excessive CPU usage
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get the latest frame"""
        with self.lock:
            return self.frame.copy() if self.frame is not None else None
    
    def stop(self):
        """Stop camera capture and cleanup"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
        print("Camera stopped")
    
    def is_running(self) -> bool:
        """Check if camera is running"""
        return self.running and self.cap is not None and self.cap.isOpened()