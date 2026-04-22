#!/usr/bin/env python3
"""
Indoor Floor Path Detection
Detects walkable floor space using depth estimation and plane detection
Works for indoor environments (rooms, hallways, etc.)
"""

import cv2
import numpy as np
import torch
import time

class FloorPathDetector:
    """Detect walkable floor paths in indoor environments"""
    
    def __init__(self):
        """Initialize depth estimation model"""
        print("🚀 Loading MiDaS depth estimation model...")
        
        # Load MiDaS small model (faster for real-time)
        self.model = torch.hub.load('intel-isl/MiDaS', 'MiDaS_small')
        self.model.eval()
        
        # Load transforms
        midas_transforms = torch.hub.load('intel-isl/MiDaS', 'transforms')
        self.transform = midas_transforms.small_transform
        
        print("✅ Model loaded successfully!")
    
    def detect_floor(self, image):
        """
        Detect floor area using depth estimation
        
        Args:
            image: BGR image from OpenCV
        
        Returns:
            floor_mask: binary mask where floor is detected
        """
        # Convert to RGB
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Prepare input
        input_batch = self.transform(rgb)
        
        # Predict depth
        with torch.no_grad():
            prediction = self.model(input_batch)
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=rgb.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()
        
        depth = prediction.cpu().numpy()
        
        # Normalize depth
        depth_normalized = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        
        # Floor is typically in the bottom portion and has similar depth
        h, w = depth_normalized.shape
        
        # Focus on bottom 60% of image
        bottom_region_start = int(h * 0.4)
        bottom_region = depth_normalized[bottom_region_start:, :]
        
        # Find the most common depth in bottom region (likely floor)
        hist = cv2.calcHist([bottom_region], [0], None, [256], [0, 256])
        floor_depth = np.argmax(hist)
        
        # Create floor mask - pixels with similar depth to floor
        floor_mask = np.zeros_like(depth_normalized, dtype=np.uint8)
        
        # Only consider bottom portion for floor
        depth_tolerance = 20
        floor_pixels = np.abs(depth_normalized - floor_depth) < depth_tolerance
        
        # Apply only to bottom region
        floor_mask[bottom_region_start:, :] = floor_pixels[bottom_region_start:, :] * 255
        
        # Clean up mask with morphology
        kernel = np.ones((5, 5), np.uint8)
        floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_CLOSE, kernel)
        floor_mask = cv2.morphologyEx(floor_mask, cv2.MORPH_OPEN, kernel)
        
        return floor_mask, depth_normalized
    
    def visualize_floor_path(self, image, floor_mask, alpha=0.6):
        """
        Visualize walkable floor path
        
        Args:
            image: original image
            floor_mask: binary mask of floor
            alpha: transparency
        
        Returns:
            visualization with floor highlighted
        """
        # Create colored overlay
        overlay = image.copy()
        
        # Yellow for floor path
        overlay[floor_mask > 0] = [0, 255, 255]  # Yellow in BGR
        
        # Blend
        result = cv2.addWeighted(image, alpha, overlay, 1 - alpha, 0)
        
        return result
    
    def get_path_stats(self, floor_mask):
        """Get statistics about walkable path"""
        h, w = floor_mask.shape
        total_pixels = h * w
        floor_pixels = np.sum(floor_mask > 0)
        
        floor_pct = (floor_pixels / total_pixels) * 100
        
        return {'floor': floor_pct}
    
    def get_path_direction(self, floor_mask):
        """Analyze path direction"""
        h, w = floor_mask.shape
        
        # Focus on bottom 60%
        bottom_start = int(h * 0.4)
        bottom_region = floor_mask[bottom_start:, :]
        
        # Divide into three sections
        left = bottom_region[:, :w//3]
        center = bottom_region[:, w//3:2*w//3]
        right = bottom_region[:, 2*w//3:]
        
        # Calculate floor percentage in each
        left_pct = (np.sum(left > 0) / left.size) * 100
        center_pct = (np.sum(center > 0) / center.size) * 100
        right_pct = (np.sum(right > 0) / right.size) * 100
        
        return {
            'left': left_pct,
            'center': center_pct,
            'right': right_pct
        }
    
    def get_guidance(self, path_direction):
        """Generate navigation guidance"""
        center = path_direction['center']
        left = path_direction['left']
        right = path_direction['right']
        
        if center > 40:
            return "Path ahead CLEAR", (0, 255, 255)
        elif left > center and left > right and left > 30:
            return "Path on LEFT", (0, 255, 255)
        elif right > center and right > left and right > 30:
            return "Path on RIGHT", (0, 255, 255)
        else:
            return "No clear path", (0, 0, 255)


def demo_webcam():
    """Run real-time floor path detection"""
    print("=" * 60)
    print("Indoor Floor Path Detection")
    print("=" * 60)
    print("📷 Starting webcam...")
    print("   YELLOW = Walkable floor path")
    print("   Press 'q' to quit, 'a' to adjust transparency")
    
    detector = FloorPathDetector()
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Failed to open webcam")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    alpha = 0.6
    fps_history = []
    
    print("✅ Webcam ready. Detecting floor paths...\n")
    
    while True:
        start_time = time.time()
        
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect floor
        floor_mask, depth_map = detector.detect_floor(frame)
        
        # Visualize
        result = detector.visualize_floor_path(frame, floor_mask, alpha=alpha)
        
        # Get stats
        stats = detector.get_path_stats(floor_mask)
        path_direction = detector.get_path_direction(floor_mask)
        guidance, guidance_color = detector.get_guidance(path_direction)
        
        # Calculate FPS
        fps = 1.0 / (time.time() - start_time)
        fps_history.append(fps)
        if len(fps_history) > 30:
            fps_history.pop(0)
        avg_fps = np.mean(fps_history)
        
        # Add overlays
        cv2.putText(result, f"FPS: {avg_fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.putText(result, f"Floor Path: {stats['floor']:.1f}%", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Path direction
        y = 95
        cv2.putText(result, f"Left: {path_direction['left']:.0f}%", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(result, f"Center: {path_direction['center']:.0f}%", (10, y + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(result, f"Right: {path_direction['right']:.0f}%", (10, y + 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Guidance
        cv2.putText(result, guidance, (10, result.shape[0] - 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, guidance_color, 3)
        
        # Instructions
        cv2.putText(result, "YELLOW=Floor Path | 'q'=Quit | 'a'=Alpha | 'd'=Depth", 
                   (10, result.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        cv2.imshow('Floor Path Detection', result)
        
        # Handle keyboard
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('a'):
            alpha = (alpha + 0.1) % 1.1
            if alpha < 0.1:
                alpha = 0.1
        elif key == ord('d'):
            # Show depth map
            depth_colored = cv2.applyColorMap(depth_map, cv2.COLORMAP_MAGMA)
            cv2.imshow('Depth Map', depth_colored)
    
    cap.release()
    cv2.destroyAllWindows()
    print("\n✅ Demo completed")


def main():
    """Main entry point"""
    demo_webcam()


if __name__ == "__main__":
    main()
