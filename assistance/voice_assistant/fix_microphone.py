"""
Microphone troubleshooting and setup
"""
import speech_recognition as sr
import sys
import os

def check_microphones():
    """Check available microphones"""
    print("🎤 Checking available microphones...")
    
    try:
        mic_list = sr.Microphone.list_microphone_names()
        print(f"Found {len(mic_list)} microphones:")
        
        for i, name in enumerate(mic_list):
            print(f"  {i}: {name}")
        
        return len(mic_list) > 0
        
    except Exception as e:
        print(f"❌ Error checking microphones: {e}")
        return False

def test_microphone_by_index(index=None):
    """Test specific microphone"""
    print(f"🧪 Testing microphone {index if index is not None else 'default'}...")
    
    try:
        # Create microphone object
        if index is not None:
            mic = sr.Microphone(device_index=index)
        else:
            mic = sr.Microphone()
        
        recognizer = sr.Recognizer()
        
        # Adjust settings
        recognizer.energy_threshold = 300
        recognizer.pause_threshold = 0.8
        
        print("🔧 Calibrating...")
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("🎤 Say 'hello' now! (5 seconds)")
        with mic as source:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
        
        print("🧠 Processing...")
        text = recognizer.recognize_google(audio)
        print(f"✅ Success! Heard: '{text}'")
        return True
        
    except sr.WaitTimeoutError:
        print("⏰ No speech detected")
        return False
    except sr.UnknownValueError:
        print("❌ Could not understand speech")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def find_working_microphone():
    """Find a working microphone"""
    print("🔍 Finding working microphone...")
    
    # Test default first
    print("\n--- Testing Default Microphone ---")
    if test_microphone_by_index(None):
        print("✅ Default microphone works!")
        return None
    
    # Test each microphone
    mic_list = sr.Microphone.list_microphone_names()
    for i in range(min(5, len(mic_list))):  # Test first 5
        print(f"\n--- Testing Microphone {i}: {mic_list[i][:50]}... ---")
        if test_microphone_by_index(i):
            print(f"✅ Microphone {i} works!")
            return i
    
    print("❌ No working microphone found")
    return None

def show_windows_tips():
    """Show Windows microphone troubleshooting tips"""
    print("\n💡 Windows Microphone Troubleshooting:")
    print("=" * 50)
    print("1. Check Windows microphone permissions:")
    print("   - Go to Settings > Privacy > Microphone")
    print("   - Make sure 'Allow apps to access microphone' is ON")
    print("   - Make sure Python/your IDE has microphone access")
    print()
    print("2. Check microphone in Windows Sound settings:")
    print("   - Right-click speaker icon in taskbar")
    print("   - Click 'Open Sound settings'")
    print("   - Test your microphone")
    print()
    print("3. Check if microphone is muted:")
    print("   - Look for mute button on microphone/headset")
    print("   - Check Windows volume mixer")
    print()
    print("4. Try different microphone:")
    print("   - Built-in laptop microphone")
    print("   - USB headset microphone")
    print("   - External USB microphone")
    print()
    print("5. Restart your computer and try again")

def main():
    """Main troubleshooting function"""
    print("🔧 Microphone Troubleshooting Tool")
    print("=" * 50)
    
    # Check if microphones are available
    if not check_microphones():
        print("❌ No microphones found!")
        show_windows_tips()
        return
    
    # Find working microphone
    working_mic = find_working_microphone()
    
    if working_mic is not None:
        print(f"\n🎉 Found working microphone: {working_mic}")
        print("✅ Your voice assistant should work now!")
    else:
        print("\n❌ No working microphone found")
        show_windows_tips()
        print("\n💡 After fixing microphone issues, run this script again to test")

if __name__ == "__main__":
    main()