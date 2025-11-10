"""
Test individual components of the voice assistant
"""
import speech_recognition as sr
import pyttsx3
import requests

# Configuration
GEMINI_API_KEY = "AIzaSyBBcYQyL8YJpzE1PkrJbTEcephbly1-BoU"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def test_microphone():
    """Test microphone and speech recognition"""
    print("🧪 Testing Microphone...")
    
    try:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        print("🎤 Say 'hello' when ready...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
        
        text = recognizer.recognize_google(audio)
        print(f"✅ Heard: '{text}'")
        return True
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False

def test_text_to_speech():
    """Test text-to-speech"""
    print("\n🧪 Testing Text-to-Speech...")
    
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        
        test_text = "Testing text to speech. Can you hear this?"
        print(f"🔊 Speaking: {test_text}")
        engine.say(test_text)
        engine.runAndWait()
        
        print("✅ Text-to-speech working")
        return True
        
    except Exception as e:
        print(f"❌ Text-to-speech test failed: {e}")
        return False

def test_gemini_api():
    """Test Gemini AI API"""
    print("\n🧪 Testing Gemini AI API...")
    
    try:
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': GEMINI_API_KEY
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": "Say 'API test successful' if you can read this."
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['candidates'][0]['content']['parts'][0]['text']
            print(f"✅ AI Response: {ai_response}")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Voice Assistant Component Tests")
    print("=" * 40)
    
    tests = [
        ("Gemini AI API", test_gemini_api),
        ("Text-to-Speech", test_text_to_speech),
        ("Microphone", test_microphone)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST RESULTS:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:15} {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Voice assistant is ready!")
        print("💡 Run: python voice_assistant.py")
    else:
        print("\n⚠️ Some tests failed. Fix issues before running assistant.")

if __name__ == "__main__":
    main()