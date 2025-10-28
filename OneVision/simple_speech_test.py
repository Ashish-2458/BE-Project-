#!/usr/bin/env python3
"""
Simple speech test with maximum volume and different methods
"""

import subprocess
import time
import os

def test_loud_speech():
    """Test speech with maximum volume"""
    print("🔊 Testing LOUD speech...")
    
    methods = [
        # Method 1: PowerShell with max volume
        '''powershell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Volume = 100; $speak.Rate = -2; $speak.Speak('LOUD TEST - CAN YOU HEAR THIS VERY LOUD SPEECH?')"''',
        
        # Method 2: VBScript with max volume
        '''cscript //nologo -e:vbscript -c:"Set s=CreateObject(""SAPI.SpVoice""):s.Volume=100:s.Rate=-2:s.Speak(""LOUD VBSCRIPT TEST - CAN YOU HEAR THIS?"")"''',
        
        # Method 3: Windows narrator command
        '''narrator /speak "NARRATOR TEST - CAN YOU HEAR THIS?"''',
    ]
    
    for i, method in enumerate(methods, 1):
        print(f"\nMethod {i}: Testing...")
        try:
            result = subprocess.run(method, shell=True, timeout=15, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Method {i} completed successfully")
            else:
                print(f"❌ Method {i} failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Method {i} error: {e}")
        
        time.sleep(2)

def create_audio_batch_file():
    """Create a batch file for audio testing"""
    batch_content = '''@echo off
echo Testing Windows Speech...
powershell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Volume = 100; $speak.Rate = 0; $speak.Speak('This is a batch file speech test. Can you hear this audio?')"
pause
'''
    
    with open('test_speech.bat', 'w') as f:
        f.write(batch_content)
    
    print("📁 Created test_speech.bat file")
    print("💡 Try double-clicking test_speech.bat to test audio")

if __name__ == "__main__":
    print("🔊 MAXIMUM VOLUME SPEECH TEST")
    print("=" * 50)
    
    # Make sure volume is up
    print("🔊 Setting system volume to maximum...")
    try:
        subprocess.run('''powershell -Command "(New-Object -comObject WScript.Shell).SendKeys([char]175)"''', shell=True, timeout=5)
        time.sleep(1)
    except:
        pass
    
    test_loud_speech()
    create_audio_batch_file()
    
    print("\n" + "=" * 50)
    print("🎧 IMPORTANT CHECKS:")
    print("1. Are your speakers/headphones turned ON?")
    print("2. Is the volume knob on speakers turned up?")
    print("3. Are headphones plugged in correctly?")
    print("4. Try running test_speech.bat")
    print("5. Check Windows volume mixer (right-click speaker icon)")