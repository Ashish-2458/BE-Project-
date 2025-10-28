"""
Quick test for speech engine only
"""
import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from speech_engine import SpeechEngine

def test_speech():
    print("🧪 Testing Speech Engine...")
    
    speech = SpeechEngine()
    
    # Test immediate speech
    print("Testing immediate speech...")
    speech.speak_immediate("Hello! This is a speech test. Can you hear me?")
    
    time.sleep(2)
    
    # Test queued speech
    print("Testing queued speech...")
    speech.speak("This is the first queued message.")
    speech.speak("This is the second queued message.")
    speech.speak("This is the third queued message.")
    
    # Wait for completion
    print("Waiting for speech to complete...")
    speech.wait_until_done(timeout=15)
    
    print("✅ Speech test completed")
    speech.shutdown()

if __name__ == "__main__":
    test_speech()