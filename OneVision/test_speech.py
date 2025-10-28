#!/usr/bin/env python3
"""
Simple speech test to verify TTS is working
"""

import time
import pyttsx3

def test_basic_speech():
    """Test basic pyttsx3 functionality"""
    print("🧪 Testing basic speech...")
    
    try:
        engine = pyttsx3.init()
        
        # Get available voices
        voices = engine.getProperty('voices')
        print(f"Available voices: {len(voices) if voices else 0}")
        
        if voices:
            for i, voice in enumerate(voices[:3]):  # Show first 3 voices
                print(f"  Voice {i}: {voice.name}")
        
        # Test speech
        print("🔊 Testing speech output...")
        engine.say("Testing speech system. Can you hear this?")
        engine.runAndWait()
        
        print("✅ Basic speech test completed")
        return True
        
    except Exception as e:
        print(f"❌ Basic speech test failed: {e}")
        return False

def test_speech_module():
    """Test our custom speech module"""
    print("🧪 Testing custom speech module...")
    
    try:
        from modules.speech import TextToSpeech
        
        tts = TextToSpeech()
        
        print("🔊 Testing custom speech...")
        tts.speak("Custom speech module test. This should be heard clearly.")
        
        # Wait for speech to complete
        time.sleep(5)
        
        tts.shutdown()
        
        print("✅ Custom speech test completed")
        return True
        
    except Exception as e:
        print(f"❌ Custom speech test failed: {e}")
        return False

def main():
    print("🎤 Speech System Test\n")
    
    # Test 1: Basic pyttsx3
    basic_works = test_basic_speech()
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Custom module
    custom_works = test_speech_module()
    
    print("\n" + "="*50)
    print("RESULTS:")
    print(f"Basic pyttsx3: {'✅ WORKING' if basic_works else '❌ FAILED'}")
    print(f"Custom module: {'✅ WORKING' if custom_works else '❌ FAILED'}")
    
    if not basic_works:
        print("\n💡 TROUBLESHOOTING:")
        print("1. Check if speakers/headphones are connected")
        print("2. Check Windows sound settings")
        print("3. Try: pip uninstall pyttsx3 && pip install pyttsx3")
        print("4. Restart your computer")

if __name__ == "__main__":
    main()