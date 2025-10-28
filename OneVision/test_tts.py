#!/usr/bin/env python3
"""
Simple test script to check if text-to-speech is working
"""

import pyttsx3
import time

def test_basic_tts():
    """Test basic pyttsx3 functionality"""
    print("Testing basic text-to-speech...")
    
    try:
        engine = pyttsx3.init()
        
        # Get available voices
        voices = engine.getProperty('voices')
        print(f"Available voices: {len(voices) if voices else 0}")
        
        if voices:
            for i, voice in enumerate(voices):
                print(f"  {i}: {voice.name} - {voice.id}")
        
        # Test speech
        print("Testing speech...")
        engine.say("Hello, this is a test of the text to speech system.")
        engine.runAndWait()
        print("Speech test completed")
        
        return True
        
    except Exception as e:
        print(f"TTS Error: {e}")
        return False

def test_windows_sapi():
    """Test Windows SAPI directly"""
    print("\nTesting Windows SAPI...")
    
    try:
        import win32com.client
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Speak("This is a Windows SAPI test")
        print("Windows SAPI test completed")
        return True
    except Exception as e:
        print(f"Windows SAPI Error: {e}")
        return False

if __name__ == "__main__":
    print("🔊 Text-to-Speech Test")
    print("=" * 30)
    
    # Test basic pyttsx3
    basic_works = test_basic_tts()
    
    # Test Windows SAPI if on Windows
    import sys
    if sys.platform == 'win32':
        sapi_works = test_windows_sapi()
    else:
        sapi_works = False
    
    print("\n" + "=" * 30)
    print("Results:")
    print(f"  Basic pyttsx3: {'✅ Working' if basic_works else '❌ Failed'}")
    if sys.platform == 'win32':
        print(f"  Windows SAPI: {'✅ Working' if sapi_works else '❌ Failed'}")
    
    if not basic_works and not sapi_works:
        print("\n💡 Suggestions:")
        print("  1. Check Windows audio settings")
        print("  2. Try: pip install --upgrade pyttsx3")
        print("  3. Try: pip install pywin32")
        print("  4. Restart your terminal/IDE")