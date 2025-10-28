"""
Configuration for AI Voice Assistant
"""
import os

# AI Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyBBcYQyL8YJpzE1PkrJbTEcephbly1-BoU')
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# Speech Recognition Settings
SPEECH_RECOGNITION_TIMEOUT = 5  # seconds to wait for speech
SPEECH_RECOGNITION_PHRASE_TIMEOUT = 1  # seconds of silence to end phrase
WAKE_WORDS = ["hey assistant", "voice assistant", "help me"]

# Text-to-Speech Settings
TTS_RATE = 150  # Words per minute
TTS_VOLUME = 0.9  # Volume level (0.0 to 1.0)

# Assistant Behavior
MAX_CONVERSATION_HISTORY = 10  # Number of exchanges to remember
RESPONSE_MAX_LENGTH = 200  # Maximum words in response
ENABLE_CONTEXT_AWARENESS = True  # Remember previous conversations

# Audio Settings
MICROPHONE_DEVICE_INDEX = None  # None for default microphone
AUDIO_CHUNK_SIZE = 1024
AUDIO_SAMPLE_RATE = 16000

# Debug Settings
DEBUG_MODE = True
LOG_CONVERSATIONS = True