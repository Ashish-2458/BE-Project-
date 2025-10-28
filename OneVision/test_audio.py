#!/usr/bin/env python3
"""
Test audio output to verify speech is working
"""

import subprocess
import time

def test_windows_audio():
    """Test Windows audio output"""
    print("🔊 Testing Windows audio output...")
    
    try:
        # Test 1: Simple beep
        print("Test 1: System beep")
        subprocess.run(['powershell', '-Command', '[console]::beep(800,500)'], timeout=3)
        time.sleep(1)
        
        # Test 2: Windows SAPI speech
        print("Test 2: Windows SAPI speech")
        cmd = '''powershell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Volume = 100; $speak.Rate = 2; $speak.Speak('Hello, can you hear this audio test?')"'''
        
        result = subprocess.run(cmd, shell=True, timeout=10, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Windows SAPI speech test completed")
        else:
            print(f"❌ Windows SAPI failed: {result.stderr}")
        
        # Test 3: VBScript method
        print("Test 3: VBScript speech")
        vbs_content = '''
        Set speech = CreateObject("SAPI.SpVoice")
        speech.Volume = 100
        speech.Rate = 2
        speech.Speak "This is a VBScript audio test"
        '''
        
        with open('audio_test.vbs', 'w') as f:
            f.write(vbs_content)
        
        result = subprocess.run(['cscript', '//nologo', 'audio_test.vbs'], timeout=10)
        
        import os
        os.remove('audio_test.vbs')
        
        if result.returncode == 0:
            print("✅ VBScript speech test completed")
        else:
            print("❌ VBScript speech failed")
        
        print("\n🎧 Did you hear any of these audio tests?")
        print("If not, check:")
        print("1. Volume is turned up")
        print("2. Speakers/headphones are connected")
        print("3. Windows audio service is running")
        
    except Exception as e:
        print(f"❌ Audio test error: {e}")

def test_pyttsx3():
    """Test pyttsx3 specifically"""
    print("\n🔊 Testing pyttsx3...")
    
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        
        print("Speaking with pyttsx3...")
        engine.say("This is a pyttsx3 audio test. Can you hear this?")
        engine.runAndWait()
        
        print("✅ pyttsx3 test completed")
        
    except Exception as e:
        print(f"❌ pyttsx3 test failed: {e}")

if __name__ == "__main__":
    print("🎤 AUDIO OUTPUT TEST")
    print("=" * 50)
    
    test_windows_audio()
    test_pyttsx3()
    
    print("\n" + "=" * 50)
    print("🎧 IMPORTANT: Did you hear ANY audio?")
    print("If NO audio was heard:")
    print("1. Check Windows volume mixer")
    print("2. Try different speakers/headphones") 
    print("3. Check Windows audio drivers")
    print("4. Restart audio service: services.msc -> Windows Audio")