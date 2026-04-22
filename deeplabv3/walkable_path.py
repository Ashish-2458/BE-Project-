#!/usr/bin/env python3
"""
Fast Walkable Path Detection using LRASPP-MobileNet v3
Real-time detection of roads, sidewalks, and walkable surfaces
Optimized for CPU performance
"""

import cv2
import numpy as np
import torch
import torchvision.transforms as T
from torchvision.models.segmentation import lraspp_mobilenet_v3_large
import time

class WalkablePathDetector:
    """Fast walkable path detection using LRASPP-MobileNet v3"""
    
    # Cityscapes class names (19 classes)
    CLASS_NAMES = [
        'road', 'sidewalk', 'building', 'wall', 'fence', 'pole',
        'traffic light', 'traffic sign', 'vegetation', 'terrain',
        'sky', 'person', 'rider', 'car', 'truck', 'bus',
        'train', 'motorcycle', 'bicycle'
    ]
    
    # Define walkable classes
    WALKABLE_CLASSES = {0, 1, 9}  # road, sidewalk, terrain
    OBSTACLE_CLASSES = {11, 12, 13, 14, 15, 16, 17, 18}  # person, rider, vehicles
    
    def __init__(self, device='auto'):
        """Initialize LRASPP model"""
        print("🚀 Loading LRASPP-MobileNet v3 model...")
        
        # Auto-detect device
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        print(f"   Using device: {self.device}")
        
        # Load pre-trained model with Cityscapes weights
        self.model = lraspp_mobilenet_v3_large(weights='DEFAULT')
        self.model.to(self.device)
        self.model.eval()
        
        # Image preprocessing
        self.transform = T.Compose([
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        print("✅ Model loaded successfully!")
    
    def segment(self, image):
        """
        Perform segmentation on an image
        
        Args:
            image: numpy array (BGR format from OpenCV)
        
        Returns:
            segmentation_map: numpy array of class indices
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Preprocess
        input_tensor = self.transform(rgb_image)
        input_batch = input_tensor.unsqueeze(0).to(self.device)
        
        # Inference
        with torch.no_grad():
            output = self.model(input_batch)['out'][0]
        
        # Get class predictions
        segmentation_map = output.argmax(0).cpu().numpy()
        
        return segmentation_map
    
    def visualize_walkable_path(self, image, segmentation_map, alpha=0.6):
        """
        Visualize walkable path - GREEN for walkable, RED for obstacles
        
        Args:
            image: original image
            segmentation_map: class indices for each pixel
            alpha: transparency
        
        Returns:
            blended image with path overlay
        """
        h, w = segmentation_map.shape
        
        # Create colored mask
        path_mask = np.zeros((h, w, 3), dtype=np.uint8)
        
        # GREEN for walkable surfaces (road, sidewalk, terrain)
        for class_idx in self.WALKABLE_CLASSES:
            path_mask[segmentation_map == class_idx] = [0, 255, 0]  # Green
        
        # RED for obstacles (people, vehicles)
        for class_idx in self.OBSTACLE_CLASSES:
            path_mask[segmentation_map == class_idx] = [0, 0, 255]  # Red
        
        # Resize to match original image
        if path_mask.shape[:2] != image.shape[:2]:
            path_mask = cv2.resize(path_mask, (image.shape[1], image.shape[0]))
        
        # Blend with original image
        blended = cv2.addWeighted(image, alpha, path_mask, 1 - alpha, 0)
        
        return blended
    
    def get_walkable_stats(self, segmentation_map):
        """Get statistics about walkable area"""
        total_pixels = segmentation_map.size
        
        # Count walkable pixels
        walkable_pixels = sum(np.sum(segmentation_map == cls) for cls in self.WALKABLE_CLASSES)
        walkable_pct = (walkable_pixels / total_pixels) * 100
        
        # Count obstacles
        obstacle_pixels = sum(np.sum(segmentation_map == cls) for cls in self.OBSTACLE_CLASSES)
        obstacle_pct = (obstacle_pixels / total_pixels) * 100
        
        return {
            'walkable': walkable_pct,
            'obstacles': obstacle_pct
        }
    
    def get_path_direction(self, segmentation_map):
        """
        Analyze path direction (left, center, right)
        
        Returns:
            dict with walkable percentages for each direction
        """
        h, w = segmentation_map.shape
        
        # Focus on bottom 70% (where ground is visible)
        ground_start = int(h * 0.3)
        ground_region = segmentation_map[ground_start:, :]
        
        # Divide into three sections
        left = ground_region[:, :w//3]
        center = ground_region[:, w//3:2*w//3]
        right = ground_region[:, 2*w//3:]
        
        # Calculate walkable percentage in each section
        def calc_walkable(section):
            walkable = sum(np.sum(section == cls) for cls in self.WALKABLE_CLASSES)
            return (walkable / section.size) * 100
        
        return {
            'left': calc_walkable(left),
            'center': calc_walkable(center),
            'right': calc_walkable(right)
        }
    
    def get_guidance(self, path_direction):
        """Generate navigation guidance based on path analysis"""
        center = path_direction['center']
        left = path_direction['left']
        right = path_direction['right']
        
        if center > 50:
            return "Path ahead CLEAR", (0, 255, 0)
        elif left > center and left > right and left > 40:
            return "Go LEFT", (0, 255, 255)
        elif right > center and right > left and right > 40:
            return "Go RIGHT", (0, 255, 255)
        elif max(left, center, right) < 30:
            return "BLOCKED - Stop", (0, 0, 255)
        else:
            return "Proceed with caution", (0, 165, 255)


def demo_webcam():
    """Run real-time walkable path detection"""
    print("=" * 60)
    print("Walkable Path Detection - LRASPP MobileNet v3")
    print("=" * 60)
    print("📷 Starting webcam...")
    print("   GREEN = Walkable (road/sidewalk)")
    print("   RED = Obstacles (people/vehicles)")
    print("   Press 'q' to quit, 'a' to adjust transparency")
    
    # Initialize detector
    detector = WalkablePathDetector()
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Failed to open webcam")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    alpha = 0.6
    fps_history = []
    
    print("✅ Webcam ready. Detecting walkable paths...\n")
    
    while True:
        start_time = time.time()
        
        ret, frame = cap.read()
        if not ret:
            break
        
        # Perform segmentation
        segmentation_map = detector.segment(frame)
        
        # Visualize
        result = detector.visualize_walkable_path(frame, segmentation_map, alpha=alpha)
        
        # Get statistics
        stats = detector.get_walkable_stats(segmentation_map)
        path_direction = detector.get_path_direction(segmentation_map)
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
        
        cv2.putText(result, f"Walkable: {stats['walkable']:.1f}%", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.putText(result, f"Obstacles: {stats['obstacles']:.1f}%", (10, 85),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Path direction
        y = 120
        cv2.putText(result, f"Left: {path_direction['left']:.0f}%", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(result, f"Center: {path_direction['center']:.0f}%", (10, y + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(result, f"Right: {path_direction['right']:.0f}%", (10, y + 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Guidance (large text)
        cv2.putText(result, guidance, (10, result.shape[0] - 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, guidance_color, 3)
        
        # Instructions
        cv2.putText(result, "GREEN=Walkable | RED=Obstacles | 'q'=Quit | 'a'=Alpha", 
                   (10, result.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        cv2.imshow('Walkable Path Detection', result)
        
        # Handle keyboard
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('a'):
            alpha = (alpha + 0.1) % 1.1
            if alpha < 0.1:
                alpha = 0.1
    
    cap.release()
    cv2.destroyAllWindows()
    print("\n✅ Demo completed")


def demo_image(image_path):
    """Process a single image"""
    print(f"🖼️  Processing: {image_path}")
    
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Failed to load: {image_path}")
        return
    
    detector = WalkablePathDetector()
    
    print("🔍 Detecting walkable paths...")
    start = time.time()
    segmentation_map = detector.segment(image)
    elapsed = time.time() - start
    
    stats = detector.get_walkable_stats(segmentation_map)
    path_direction = detector.get_path_direction(segmentation_map)
    guidance, _ = detector.get_guidance(path_direction)
    
    print(f"✅ Completed in {elapsed:.2f}s")
    print(f"   Walkable: {stats['walkable']:.1f}%")
    print(f"   Obstacles: {stats['obstacles']:.1f}%")
    print(f"   Guidance: {guidance}")
    
    result = detector.visualize_walkable_path(image, segmentation_map)
    
    cv2.imshow('Original', image)
    cv2.imshow('Walkable Path', result)
    print("\n👁️  Press any key to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        demo_image(sys.argv[1])
    else:
        demo_webcam()


if __name__ == "__main__":
    main()
