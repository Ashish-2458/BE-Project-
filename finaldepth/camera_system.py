"""
Camera feed management system
"""
import cv2
import numpy as np
from threading import Thread, Lock
import time
from config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, FPS

class CameraSystem:
    def __init__(self):
        self.cap = None
        self.frame = None
        self.frame_lock = Lock()
        self.running = False
        self.thread = None
        
    def start(self):
        """Start camera capture"""
        try:
            self.cap = cv2.VideoCapture(CAMERA_INDEX)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, FPS)
            
            if not self.cap.isOpened():
                raise Exception("Could not open camera")
                
            self.running = True
            self.thread = Thread(target=self._capture_loop)
            self.thread.daemon = True
            self.thread.start()
            
            print("Camera system started successfully")
            return True
            
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False
    
    def _capture_loop(self):
        """Continuous frame capture loop"""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.frame_lock:
                    self.frame = frame.copy()
            time.sleep(1/FPS)
    
    def get_frame(self):
        """Get current frame"""
        with self.frame_lock:
            return self.frame.copy() if self.frame is not None else None
    
    def stop(self):
        """Stop camera capture gracefully"""
        print("Stopping camera...")
        self.running = False
        
        # Wait for thread with timeout
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        # Release camera with error handling
        if self.cap:
            try:
                self.cap.release()
                print("Camera released successfully")
            except Exception as e:
                print(f"Camera release warning: {e}")
        
        print("Camera system stopped")