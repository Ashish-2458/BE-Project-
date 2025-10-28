import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyAFfnD2wOiRQE2RcIkgxh6UpS_eGP1FXjc"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Camera Configuration
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30

# YOLO Configuration
YOLO_MODEL = "yolov8n.pt"  # Nano model for speed
CONFIDENCE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.45

# Speech Configuration
SPEECH_RATE = 150  # Words per minute
SPEECH_VOLUME = 0.9

# Processing Configuration
DETECTION_INTERVAL = 1.0  # Fast detection for responsive feedback
MAX_OBJECTS_TO_DESCRIBE = 6  # Focus on most important objects for speed
SCENE_UPDATE_THRESHOLD = 2  # Sensitive to changes