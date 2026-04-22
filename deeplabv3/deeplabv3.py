#!/usr/bin/env python3
"""
DeepLab v3 Semantic Segmentation Demo
Pixel-level scene understanding for assistive vision applications
"""

import cv2
import numpy as np
import torch
import torchvision.transforms as T
from torchvision.models.segmentation import deeplabv3_resnet101
import time
from PIL import Image

class DeepLabV3Segmenter:
    """DeepLab v3 semantic segmentation wrapper"""
    
    # COCO/Pascal VOC class names (21 classes)
    CLASS_NAMES = [
        'background', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus',
        'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike',
        'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor'
    ]
    
    # Define walkable vs non-walkable classes
    WALKABLE_CLASSES = {
        0: 'background'  # Floor, ground, sidewalk, road (usually background)
    }
    
    OBSTACLES = {
        1: 'aeroplane', 2: 'bicycle', 3: 'bird', 4: 'boat', 5: 'bottle', 
        6: 'bus', 7: 'car', 8: 'cat', 9: 'chair', 10: 'cow', 
        11: 'diningtable', 12: 'dog', 13: 'horse', 14: 'motorbike',
        15: 'person', 16: 'pottedplant', 17: 'sheep', 18: 'sofa', 
        19: 'train', 20: 'tvmonitor'
    }
    
    # Color map for visualization (BGR format for OpenCV)
    COLORS = np.array([
        [0, 0, 0],       # background - black
        [128, 0, 0],     # aeroplane - dark red
        [0, 128, 0],     # bicycle - dark green
        [128, 128, 0],   # bird - olive
        [0, 0, 128],     # boat - dark blue
        [128, 0, 128],   # bottle - purple
        [0, 128, 128],   # bus - teal
        [128, 128, 128], # car - gray
        [64, 0, 0],      # cat - maroon
        [192, 0, 0],     # chair - red
        [64, 128, 0],    # cow - yellow-green
        [192, 128, 0],   # diningtable - orange
        [64, 0, 128],    # dog - purple-blue
        [192, 0, 128],   # horse - magenta
        [64, 128, 128],  # motorbike - cyan
        [192, 128, 128], # person - pink
        [0, 64, 0],      # pottedplant - dark green
        [128, 64, 0],    # sheep - brown
        [0, 192, 0],     # sofa - bright green
        [128, 192, 0],   # train - lime
        [0, 64, 128]     # tvmonitor - blue
    ], dtype=np.uint8)
    
    def __init__(self, device='auto', use_half_precision=False):
        """Initialize DeepLab v3 model"""
        print("🧠 Loading DeepLab v3 model...")
        
        # Auto-detect device
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        print(f"   Using device: {self.device}")
        
        # Load pre-trained model
        self.model = deeplabv3_resnet101(weights='DEFAULT')
        self.model.to(self.device)
        self.model.eval()
        
        # Use half precision for faster inference on GPU
        self.use_half = use_half_precision and self.device.type == 'cuda'
        if self.use_half:
            self.model.half()
            print("   Using half precision (FP16)")
        
        # Image preprocessing
        self.transform = T.Compose([
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        print("✅ Model loaded successfully!")
    
    def segment(self, image, resize_for_speed=True):
        """
        Perform semantic segmentation on an image
        
        Args:
            image: numpy array (BGR format from OpenCV)
            resize_for_speed: resize to smaller size for faster processing
        
        Returns:
            segmentation_map: numpy array of class indices
        """
        original_shape = image.shape[:2]
        
        # Resize for faster processing on CPU
        if resize_for_speed and self.device.type == 'cpu':
            image = cv2.resize(image, (320, 240))
        
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Preprocess
        input_tensor = self.transform(rgb_image)
        input_batch = input_tensor.unsqueeze(0).to(self.device)
        
        if self.use_half:
            input_batch = input_batch.half()
        
        # Inference
        with torch.no_grad():
            output = self.model(input_batch)['out'][0]
        
        # Get class predictions
        segmentation_map = output.argmax(0).cpu().numpy()
        
        # Resize back to original if needed
        if resize_for_speed and self.device.type == 'cpu':
            segmentation_map = cv2.resize(segmentation_map, 
                                         (original_shape[1], original_shape[0]), 
                                         interpolation=cv2.INTER_NEAREST)
        
        return segmentation_map
    
    def visualize_walkable_path(self, image, segmentation_map, alpha=0.5):
        """
        Visualize walkable path - GREEN for safe, RED for obstacles
        
        Args:
            image: original image
            segmentation_map: class indices for each pixel
            alpha: transparency
        
        Returns:
            image with walkable path overlay
        """
        h, w = segmentation_map.shape
        
        # Create binary mask: walkable (green) vs obstacles (red)
        walkable_mask = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Green for walkable areas (background/floor)
        walkable_mask[segmentation_map == 0] = [0, 255, 0]  # Bright green
        
        # Red for obstacles (everything else)
        for class_idx in range(1, len(self.CLASS_NAMES)):
            walkable_mask[segmentation_map == class_idx] = [0, 0, 255]  # Red
        
        # Resize to match original image
        if walkable_mask.shape[:2] != image.shape[:2]:
            walkable_mask = cv2.resize(walkable_mask, (image.shape[1], image.shape[0]))
        
        # Blend with original image
        blended = cv2.addWeighted(image, alpha, walkable_mask, 1 - alpha, 0)
        
        return blended
    
    def get_walkable_percentage(self, segmentation_map):
        """Calculate percentage of walkable area in view"""
        total_pixels = segmentation_map.size
        walkable_pixels = np.sum(segmentation_map == 0)
        return (walkable_pixels / total_pixels) * 100
    
    def get_path_direction(self, segmentation_map):
        """
        Analyze where the walkable path is (left, center, right)
        
        Returns:
            dict with left, center, right walkable percentages
        """
        h, w = segmentation_map.shape
        
        # Divide into three vertical sections
        left_section = segmentation_map[:, :w//3]
        center_section = segmentation_map[:, w//3:2*w//3]
        right_section = segmentation_map[:, 2*w//3:]
        
        # Calculate walkable percentage in each section
        left_walkable = (np.sum(left_section == 0) / left_section.size) * 100
        center_walkable = (np.sum(center_section == 0) / center_section.size) * 100
        right_walkable = (np.sum(right_section == 0) / right_section.size) * 100
        
        return {
            'left': left_walkable,
            'center': center_walkable,
            'right': right_walkable
        }
    
    def get_scene_stats(self, segmentation_map):
        """Get statistics about detected classes"""
        unique, counts = np.unique(segmentation_map, return_counts=True)
        total_pixels = segmentation_map.size
        
        stats = []
        for class_idx, count in zip(unique, counts):
            if class_idx == 0:  # Skip background
                continue
            percentage = (count / total_pixels) * 100
            if percentage > 1.0:  # Only report if >1% of image
                stats.append({
                    'class': self.CLASS_NAMES[class_idx],
                    'percentage': percentage,
                    'pixels': count
                })
        
        # Sort by percentage
        stats.sort(key=lambda x: x['percentage'], reverse=True)
        return stats


def demo_webcam():
    """Run real-time walkable path detection on webcam feed"""
    print("📷 Starting walkable path detection...")
    print("   GREEN = Safe to walk | RED = Obstacles")
    print("   Press 'q' to quit, 'a' to adjust alpha")
    
    # Initialize segmenter
    segmenter = DeepLabV3Segmenter()
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Failed to open webcam")
        return
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    alpha = 0.5
    fps_history = []
    
    print("✅ Webcam opened. Detecting walkable paths...")
    
    while True:
        start_time = time.time()
        
        ret, frame = cap.read()
        if not ret:
            break
        
        # Perform segmentation
        segmentation_map = segmenter.segment(frame)
        
        # Visualize walkable path
        result = segmenter.visualize_walkable_path(frame, segmentation_map, alpha=alpha)
        
        # Get path analysis
        walkable_pct = segmenter.get_walkable_percentage(segmentation_map)
        path_direction = segmenter.get_path_direction(segmentation_map)
        
        # Calculate FPS
        fps = 1.0 / (time.time() - start_time)
        fps_history.append(fps)
        if len(fps_history) > 30:
            fps_history.pop(0)
        avg_fps = np.mean(fps_history)
        
        # Add info overlay
        cv2.putText(result, f"FPS: {avg_fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(result, f"Walkable: {walkable_pct:.1f}%", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Path direction indicators
        y_pos = 90
        cv2.putText(result, f"Left: {path_direction['left']:.0f}%", (10, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(result, f"Center: {path_direction['center']:.0f}%", (10, y_pos + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(result, f"Right: {path_direction['right']:.0f}%", (10, y_pos + 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        # Guidance text
        if path_direction['center'] > 60:
            guidance = "Path ahead is CLEAR"
            color = (0, 255, 0)
        elif path_direction['left'] > path_direction['right']:
            guidance = "Path clearer on LEFT"
            color = (0, 255, 255)
        elif path_direction['right'] > path_direction['left']:
            guidance = "Path clearer on RIGHT"
            color = (0, 255, 255)
        else:
            guidance = "OBSTACLES ahead"
            color = (0, 0, 255)
        
        cv2.putText(result, guidance, (10, result.shape[0] - 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        cv2.putText(result, "GREEN=Safe | RED=Obstacles | Press 'q' to quit", 
                   (10, result.shape[0] - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow('Walkable Path Detection', result)
        
        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('a'):
            alpha = (alpha + 0.1) % 1.1
            if alpha < 0.1:
                alpha = 0.1
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Demo completed")


def demo_image(image_path):
    """Run segmentation on a single image"""
    print(f"🖼️  Processing image: {image_path}")
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Failed to load image: {image_path}")
        return
    
    # Initialize segmenter
    segmenter = DeepLabV3Segmenter()
    
    # Perform segmentation
    print("🔍 Running segmentation...")
    start_time = time.time()
    segmentation_map = segmenter.segment(image)
    elapsed = time.time() - start_time
    print(f"✅ Segmentation completed in {elapsed:.2f}s")
    
    # Get statistics
    stats = segmenter.get_scene_stats(segmentation_map)
    print("\n📊 Scene composition:")
    for stat in stats:
        print(f"   {stat['class']}: {stat['percentage']:.1f}%")
    
    # Visualize
    result = segmenter.visualize(image, segmentation_map, alpha=0.6)
    
    # Display
    cv2.imshow('Original', image)
    cv2.imshow('Segmentation', result)
    print("\n👁️  Press any key to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    """Main entry point"""
    import sys
    
    print("=" * 60)
    print("DeepLab v3 Walkable Path Detection")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Image mode
        image_path = sys.argv[1]
        demo_image(image_path)
    else:
        # Webcam mode
        demo_webcam()


if __name__ == "__main__":
    main()
