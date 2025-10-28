"""
Test microphone and speech recognition
"""
import speech_recognition as sr
import time

def test_microphone():
    """Test microphone input"""
    print("🎤 Testing Microphone")
    print("=" * 30)
    
    # Initialize recognizer and microphone
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    print("🎤 Available microphones:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  {index}: {name}")
    
    print(f"\n🎤 Using default microphone")
    
    # Adjust for ambient noise
    print("🔧 Adjusting for ambient noise... (stay quiet)")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=2)
    print("✅ Microphone calibrated")
    
    # Test listening
    for i in range(3):
        print(f"\n--- Test {i+1}/3 ---")
        print("🎤 Say something now! (You have 10 seconds)")
        
        try:
            with microphone as source:
                # Listen for audio
                audio = recognizer.listen(
                    source, 
                    timeout=10,  # Wait 10 seconds for speech
                    phrase_time_limit=10  # Allow 10 seconds of speech
                )
            
            print("🧠 Converting speech to text...")
            
            # Try to recognize speech
            try:
                text = recognizer.recognize_google(audio)
                print(f"✅ You said: '{text}'")
            except sr.UnknownValueError:
                print("❌ Could not understand the audio")
            except sr.RequestError as e:
                print(f"❌ Speech recognition service error: {e}")
                
        except sr.WaitTimeoutError:
            print("⏰ No speech detected in 10 seconds")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(1)
    
    print("\n🎤 Microphone test completed!")

if __name__ == "__main__":
    test_microphone()