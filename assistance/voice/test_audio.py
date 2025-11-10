"""
Test audio output to make sure you can hear sounds
"""
import sys
import os
import time

# Add path to OneVision
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def test_windows_sapi():
    """Test Windows SAPI directly"""
    print("🧪 Testing Windows SAPI...")
    
    try:
        import win32com.client
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Volume = 100  # Maximum volume
        speaker.Rate = 0  # Normal speed
        
        test_text = "LOUD AUDIO TEST - CAN YOU HEAR THIS VERY LOUD VOICE?"
        print(f"🔊 Speaking LOUDLY: {test_text}")
        speaker.Speak(test_text)
        
        print("✅ Windows SAPI test completed")
        return True
        
    except Exception as e:
        print(f"❌ Windows SAPI failed: {e}")
        return False

def test_pyttsx3():
    """Test pyttsx3"""
    print("\n🧪 Testing pyttsx3...")
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)  # Maximum volume
        
        test_text = "PYTTSX3 AUDIO TEST - CAN YOU HEAR THIS?"
        print(f"🔊 Speaking: {test_text}")
        engine.say(test_text)
        engine.runAndWait()
        
        print("✅ pyttsx3 test completed")
        return True
        
    except Exception as e:
        print(f"❌ pyttsx3 failed: {e}")
        return False

def test_onevision_tts():
    """Test OneVision TTS system"""
    print("\n🧪 Testing OneVision TTS...")
    
    try:
        from OneVision.modules.speech import TextToSpeech
        
        tts = TextToSpeech(rate=150, volume=0.9)
        
        test_text = "ONEVISION TTS TEST - THIS SHOULD BE LOUD AND CLEAR!"
        print(f"🔊 Speaking: {test_text}")
        tts.speak_immediate(test_text)
        
        time.sleep(5)  # Wait for speech
        tts.shutdown()
        
        print("✅ OneVision TTS test completed")
        return True
        
    except Exception as e:
        print(f"❌ OneVision TTS failed: {e}")
        return False

def check_windows_volume():
    """Check Windows volume settings"""
    print("\n🔊 Windows Audio Checklist:")
    print("=" * 40)
    print("1. Check speaker/headphone connection")
    print("2. Check Windows volume (should be 50% or higher)")
    print("3. Right-click speaker icon → Open Volume mixer")
    print("4. Make sure Python is not muted in volume mixer")
    print("5. Try different speakers/headphones")
    print("6. Check if speakers are powered on")

def main():
    """Test all audio methods"""
    print("🔊 AUDIO TEST SUITE")
    print("=" * 50)
    print("Testing different audio methods to find what works...")
    
    tests = [
        ("Windows SAPI", test_windows_sapi),
        ("pyttsx3", test_pyttsx3),
        ("OneVision TTS", test_onevision_tts)
    ]
    
    working_methods = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                working_methods.append(test_name)
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
    
    # Results
    print("\n" + "=" * 50)
    print("AUDIO TEST RESULTS:")
    print("=" * 50)
    
    if working_methods:
        print("✅ Working audio methods:")
        for method in working_methods:
            print(f"  - {method}")
        print("\n🎉 At least one audio method is working!")
    else:
        print("❌ NO AUDIO METHODS WORKING!")
        check_windows_volume()
        print("\n💡 Try:")
        print("  1. Check Windows sound settings")
        print("  2. Test with different speakers/headphones")
        print("  3. Restart your computer")
        print("  4. Check Windows audio drivers")

if __name__ == "__main__":
    main()