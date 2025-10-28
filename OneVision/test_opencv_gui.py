#!/usr/bin/env python3
"""
Test OpenCV GUI functionality
"""

import cv2
import numpy as np

def test_opencv_gui():
    """Test if OpenCV can display windows"""
    print("Testing OpenCV GUI...")
    
    try:
        # Create a test image
        img = np.zeros((300, 400, 3), dtype=np.uint8)
        cv2.putText(img, "OpenCV GUI Test", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(img, "Press 'q' to close", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        
        # Try to display the window
        cv2.imshow('OpenCV Test', img)
        print("✅ Window created successfully!")
        print("Press 'q' in the window to close it...")
        
        # Wait for key press
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        cv2.destroyAllWindows()
        print("✅ OpenCV GUI test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ OpenCV GUI test failed: {e}")
        return False

if __name__ == "__main__":
    test_opencv_gui()