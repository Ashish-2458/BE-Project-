"""
Configuration settings for Describe Scenario feature
"""

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyBBcYQyL8YJpzE1PkrJbTEcephbly1-BoU"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Camera Settings
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Real-time Mode Settings
DESCRIPTION_INTERVAL = 5.0  # seconds between descriptions (faster updates)
MAX_RETRIES = 3

# Speech Settings
SPEECH_RATE = 150  # words per minute
SPEECH_VOLUME = 0.9

# Image Processing
IMAGE_QUALITY = 85  # JPEG quality for API upload
MAX_IMAGE_SIZE = (800, 600)  # resize large images for faster processing