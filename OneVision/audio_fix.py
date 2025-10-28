#!/usr/bin/env python3
"""
Audio diagnostic and fix tool
"""

import subprocess
import time

def check_audio_devices():
    """Check available audio devices"""
    print("🔊 Checking audio devices...")
    
    try:
        cmd = '''powershell -Command "Get-AudioDevice -List | Format-Table Name, Default, Type"'''
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.stdout:
            print("Available audio devices:")
            print(result.stdout)
        else:
            print("Could not list audio devices")
            
    except Exception as e:
        print(f"Error checking devices: {e}")

def test_speech_with_different_voices():
    """Test speech with different voices"""
    print("\n🗣️ Testing different voices...")
    
    try:
        cmd = '''powershell -Command "
        Add-Type -AssemblyName System.Speech
        $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer
        
        Write-Host 'Available voices:'
        $speak.GetInstalledVoices() | ForEach-Object { Write-Host $_.VoiceInfo.Name }
        
        Write-Host 'Testing default voice...'
        $speak.Volume = 100
        $speak.Rate = 0
        $speak.Speak('Testing default voice. Can you hear this?')
        
        Write-Host 'Trying different voice...'
        $voices = $speak.GetInstalledVoices()
        if ($voices.Count -gt 1) {
            $speak.SelectVoice($voices[1].VoiceInfo.Name)
            $speak.Speak('Testing second voice. Can you hear this one?')
        }
        "'''
        
        result = subprocess.run(cmd, shell=True, timeout=20)
        print("Voice test completed")
        
    except Exception as e:
        print(f"Voice test error: {e}")

def force_audio_restart():
    """Restart Windows audio service"""
    print("\n🔄 Attempting to restart audio service...")
    
    try:
        # Stop audio service
        subprocess.run(['net', 'stop', 'audiosrv'], shell=True, timeout=10)
        time.sleep(2)
        
        # Start audio service
        subprocess.run(['net', 'start', 'audiosrv'], shell=True, timeout=10)
        time.sleep(2)
        
        print("✅ Audio service restarted")
        
        # Test after restart
        cmd = '''powershell -Command "Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Volume = 100; $speak.Speak('Audio service restarted. Testing now.')"'''
        subprocess.run(cmd, shell=True, timeout=10)
        
    except Exception as e:
        print(f"❌ Could not restart audio service: {e}")
        print("Try running as administrator")

def main():
    print("🔧 AUDIO DIAGNOSTIC TOOL")
    print("=" * 50)
    
    check_audio_devices()
    test_speech_with_different_voices()
    
    print("\n" + "=" * 50)
    print("🎧 Did you hear any speech?")
    
    response = input("Type 'y' if you heard speech, 'n' if not: ").lower()
    
    if response == 'n':
        print("\n🔧 Trying audio service restart...")
        force_audio_restart()
        
        print("\n💡 Additional troubleshooting:")
        print("1. Check if headphones/speakers are plugged in correctly")
        print("2. Try different USB ports for USB headphones")
        print("3. Update audio drivers")
        print("4. Check Windows Sound settings")
        print("5. Restart computer")
    else:
        print("✅ Great! Audio is working. The assistive vision system should work now.")

if __name__ == "__main__":
    main()