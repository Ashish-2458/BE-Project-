"""
Configuration settings for the Enhanced Vision Assistant
"""
import os

# API Configuration
GEMINI_API_KEY = "AIzaSyC1VlGVYOkeFhjsXpTYci0kk8jTeve3nIA"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# Model Paths
YOLO_MODEL_PATH = "yolov8n.pt"  # Will download automatically
DEPTH_MODEL_NAME = "LiheYoung/depth-anything-small-hf"  # Hugging Face model

# Camera Settings
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30

# Detection Settings
CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.4

# Audio Settings
TTS_RATE = 150
TTS_VOLUME = 0.9

# Spatial Settings
DISTANCE_ZONES = {
    "immediate": (0, 1.5),      # 0-1.5 meters
    "close": (1.5, 3.0),       # 1.5-3 meters  
    "medium": (3.0, 6.0),      # 3-6 meters
    "far": (6.0, float('inf')) # 6+ meters
}

# Priority Objects (for navigation assistance)
PRIORITY_OBJECTS = [
    'person', 'bicycle', 'car', 'motorcycle', 'bus', 'truck', 
    'chair', 'couch', 'bed', 'dining table', 'toilet', 'tv',
    'laptop', 'mouse', 'keyboard', 'cell phone', 'book'
]