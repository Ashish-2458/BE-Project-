"""
Quick test for voice assistant components
"""
import sys
import os

# Add paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def test_api_connection():
    """Test Gemini API connection"""
    print("🧪 Testing Gemini API connection...")
    
    try:
        import requests
        import config
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': config.GEMINI_API_KEY
        }
        
        payload = {
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
        
        response = requests.post(
            config.GEMINI_API_URL,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result:
                ai_response = result['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ API Response: {ai_response}")
                return True
        
        print(f"❌ API Error: {response.status_code}")
        return False
        
    except Exception as e:
        print(f"❌ API Test Failed: {e}")
        return False

def test_tts():
    """Test text-to-speech"""
    print("\n🧪 Testing Text-to-Speech...")
    
    try:
        from OneVision.modules.speech import TextToSpeech
        
        tts = TextToSpeech()
        tts.speak_immediate("Voice assistant test - can you hear this?")
        
        print("✅ TTS test completed")
        tts.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False

def test_conversation_manager():
    """Test conversation manager"""
    print("\n🧪 Testing Conversation Manager...")
    
    try:
        from conversation_manager import ConversationManager
        
        cm = ConversationManager()
        cm.add_exchange("Hello", "Hi! How can I help you?")
        
        context = cm.get_conversation_context()
        print(f"✅ Conversation manager working - {len(context)} exchanges")
        return True
        
    except Exception as e:
        print(f"❌ Conversation manager test failed: {e}")
        return False

def main():
    """Run quick tests"""
    print("🚀 Quick Voice Assistant Test")
    print("=" * 40)
    
    tests = [
        ("API Connection", test_api_connection),
        ("Text-to-Speech", test_tts),
        ("Conversation Manager", test_conversation_manager)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("RESULTS:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Voice assistant is ready!")
        print("💡 Run: python voice_assistant.py")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    main()