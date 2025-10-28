"""
Test script for Describe Scenario feature
"""
import time
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from camera_handler import CameraHandler
from gemini_client import GeminiClient
from speech_engine import SpeechEngine

def test_camera():
    """Test camera functionality"""
    print("🧪 Testing Camera...")
    
    camera = CameraHandler()
    if not camera.initialize():
        print("❌ Camera test failed")
        return False
        
    # Test frame capture
    frame = camera.capture_frame()
    if frame is None:
        print("❌ Frame capture failed")
        camera.release()
        return False
        
    # Test base64 encoding
    base64_image = camera.frame_to_base64(frame)
    if not base64_image:
        print("❌ Base64 encoding failed")
        camera.release()
        return False
        
    print(f"✅ Camera test passed - captured {len(base64_image)} bytes")
    camera.release()
    return True

def test_speech():
    """Test speech engine"""
    print("🧪 Testing Speech Engine...")
    
    speech = SpeechEngine()
    
    # Test immediate speech
    speech.speak_immediate("Speech engine test successful")
    
    # Test queued speech
    speech.speak("This is a queued message")
    
    # Wait for completion
    speech.wait_until_done(timeout=10)
    
    print("✅ Speech test completed")
    speech.shutdown()
    return True

def test_ai_client():
    """Test AI client (text-only)"""
    print("🧪 Testing AI Client...")
    
    client = GeminiClient()
    
    # Test connection
    if not client.test_connection():
        print("❌ AI client connection failed")
        return False
        
    print("✅ AI client test passed")
    return True

def test_full_pipeline():
    """Test complete pipeline"""
    print("🧪 Testing Full Pipeline...")
    
    # Initialize components
    camera = CameraHandler()
    ai_client = GeminiClient()
    speech = SpeechEngine()
    
    try:
        # Test camera
        if not camera.initialize():
            print("❌ Pipeline test failed - camera")
            return False
            
        # Capture image
        image_base64 = camera.capture_and_encode()
        if not image_base64:
            print("❌ Pipeline test failed - image capture")
            return False
            
        print("📸 Image captured successfully")
        
        # Get AI description
        description = ai_client.describe_image(image_base64)
        if not description:
            print("❌ Pipeline test failed - AI description")
            return False
            
        print(f"🧠 AI Description: {description}")
        
        # Speak description
        speech.speak_immediate(f"Pipeline test successful. Description: {description}")
        
        print("✅ Full pipeline test passed")
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test error: {e}")
        return False
        
    finally:
        camera.release()
        speech.shutdown()

def main():
    """Run all tests"""
    print("🧪 Describe Scenario - Test Suite")
    print("=" * 40)
    
    tests = [
        ("Camera", test_camera),
        ("Speech Engine", test_speech),
        ("AI Client", test_ai_client),
        ("Full Pipeline", test_full_pipeline)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} Test ---")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! System is ready.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)