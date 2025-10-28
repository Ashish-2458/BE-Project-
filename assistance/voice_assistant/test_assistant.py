"""
Test script for the AI Voice Assistant
"""
import sys
import os

# Add paths for imports
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import config
        print("✅ Config imported")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from accessibility_prompts import SYSTEM_PROMPT
        print("✅ Accessibility prompts imported")
    except Exception as e:
        print(f"❌ Accessibility prompts import failed: {e}")
        return False
    
    try:
        from conversation_manager import ConversationManager
        print("✅ Conversation manager imported")
    except Exception as e:
        print(f"❌ Conversation manager import failed: {e}")
        return False
    
    try:
        from OneVision.modules.speech import TextToSpeech
        print("✅ TTS module imported")
    except Exception as e:
        print(f"❌ TTS module import failed: {e}")
        return False
    
    return True

def test_conversation_manager():
    """Test conversation manager functionality"""
    print("\n🧪 Testing conversation manager...")
    
    try:
        from conversation_manager import ConversationManager
        
        cm = ConversationManager()
        
        # Test adding exchanges
        cm.add_exchange("Hello", "Hi there! How can I help you?")
        cm.add_exchange("What's the weather?", "I'd be happy to help with weather information.")
        
        # Test getting context
        context = cm.get_conversation_context()
        print(f"✅ Conversation context: {len(context)} exchanges")
        
        # Test stats
        stats = cm.get_session_stats()
        print(f"✅ Session stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversation manager test failed: {e}")
        return False

def test_tts():
    """Test text-to-speech functionality"""
    print("\n🧪 Testing text-to-speech...")
    
    try:
        from OneVision.modules.speech import TextToSpeech
        
        tts = TextToSpeech()
        tts.speak_immediate("Testing voice assistant text to speech system")
        
        print("✅ TTS test completed")
        tts.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False

def test_speech_recognition():
    """Test speech recognition (optional - requires microphone)"""
    print("\n🧪 Testing speech recognition...")
    
    try:
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        print("✅ Speech recognition modules available")
        
        # Test microphone access
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("✅ Microphone access working")
        return True
        
    except ImportError:
        print("❌ speech_recognition module not installed")
        print("💡 Install with: pip install SpeechRecognition pyaudio")
        return False
    except Exception as e:
        print(f"❌ Speech recognition test failed: {e}")
        return False

def test_ai_connection():
    """Test AI connection"""
    print("\n🧪 Testing AI connection...")
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scenario', 'describe_scenario'))
        from gemini_client import GeminiClient
        
        client = GeminiClient()
        if client.test_connection():
            print("✅ AI connection working")
            return True
        else:
            print("❌ AI connection failed")
            return False
            
    except Exception as e:
        print(f"❌ AI connection test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 AI Voice Assistant Test Suite")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Conversation Manager", test_conversation_manager),
        ("Text-to-Speech", test_tts),
        ("Speech Recognition", test_speech_recognition),
        ("AI Connection", test_ai_connection)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*50)
    print("TEST RESULTS:")
    print("="*50)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\nOverall: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 All tests passed! Voice assistant is ready to use.")
    else:
        print("⚠️ Some tests failed. Check the issues above before running the assistant.")
    
    return passed_count == total_count

if __name__ == "__main__":
    main()