#!/usr/bin/env python3
"""
Test the new speech module
"""

from modules.speech import TextToSpeech
import time

def test_speech_module():
    print("🧪 Testing new speech module...")
    
    try:
        tts = TextToSpeech()
        
        print("Testing speech...")
        tts.speak("Hello, this is a test of the new speech system. Can you hear this?")
        
        time.sleep(2)
        
        tts.speak("Testing again with different text. Navigation guidance working.")
        
        time.sleep(2)
        
        tts.shutdown()
        
        print("✅ Speech module test completed")
        
    except Exception as e:
        print(f"❌ Speech module test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_speech_module()