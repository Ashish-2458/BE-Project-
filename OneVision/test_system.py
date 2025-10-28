#!/usr/bin/env python3
"""
Test script for Assistive Vision System components
"""

import time
import sys
from modules.camera import CameraCapture
from modules.detector import ObjectDetector
from modules.llm_client import GeminiClient
from modules.speech import TextToSpeech
import config

def test_camera():
    """Test camera functionality"""
    print("🧪 Testing camera...")
    camera = CameraCapture()
    
    if camera.start():
        print("✅ Camera started successfully")
        time.sleep(2)
        
        frame = camera.get_frame()
        if frame is not None:
            print(f"✅ Frame captured: {frame.shape}")
        else:
            print("❌ No frame captured")
        
        camera.stop()
        return True
    else:
        print("❌ Camera failed to start")
        return False

def test_detector():
    """Test object detection"""
    print("🧪 Testing object detector...")
    try:
        detector = ObjectDetector()
        print("✅ YOLO model loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Detector failed: {e}")
        return False

def test_llm():
    """Test Gemini API"""
    print("🧪 Testing Gemini API...")
    try:
        client = GeminiClient(config.GEMINI_API_KEY, config.GEMINI_API_URL)
        
        # Test with sample detections
        sample_detections = [
            {
                'class_name': 'person',
                'confidence': 0.85,
                'position': 'center middle',
                'distance': 'close'
            },
            {
                'class_name': 'chair',
                'confidence': 0.72,
                'position': 'right middle',
                'distance': 'medium distance'
            }
        ]
        
        description = client.generate_scene_description(sample_detections)
        if description:
            print(f"✅ LLM response: {description}")
            return True
        else:
            print("❌ No response from LLM")
            return False
            
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False

def test_speech():
    """Test text-to-speech"""
    print("🧪 Testing text-to-speech...")
    try:
        tts = TextToSpeech()
        tts.speak("Testing speech system")
        time.sleep(3)  # Wait for speech to complete
        tts.shutdown()
        print("✅ Speech test completed")
        return True
    except Exception as e:
        print(f"❌ Speech test failed: {e}")
        return False

def test_integration():
    """Test full system integration"""
    print("🧪 Testing full system integration...")
    
    try:
        # Initialize components
        camera = CameraCapture()
        detector = ObjectDetector()
        llm_client = GeminiClient(config.GEMINI_API_KEY, config.GEMINI_API_URL)
        tts = TextToSpeech()
        
        if not camera.start():
            print("❌ Integration test failed: Camera")
            return False
        
        print("📷 Capturing and analyzing frame...")
        time.sleep(2)  # Let camera stabilize
        
        frame = camera.get_frame()
        if frame is None:
            print("❌ Integration test failed: No frame")
            camera.stop()
            return False
        
        # Detect objects
        detections = detector.detect_objects(frame)
        print(f"🔍 Detected {len(detections)} objects")
        
        if detections:
            # Generate description
            description = llm_client.generate_scene_description(detections[:5])
            if description:
                print(f"🧠 Generated description: {description}")
                tts.speak(description)
                time.sleep(5)  # Wait for speech
            else:
                print("⚠️  No description generated")
        else:
            print("ℹ️  No objects detected (this is normal)")
            tts.speak("No objects detected in current view")
            time.sleep(3)
        
        # Cleanup
        camera.stop()
        tts.shutdown()
        
        print("✅ Integration test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running Assistive Vision System Tests\n")
    
    tests = [
        ("Camera", test_camera),
        ("Object Detector", test_detector),
        ("Gemini LLM", test_llm),
        ("Text-to-Speech", test_speech),
        ("Full Integration", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print("\n🛑 Tests interrupted by user")
            break
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("🎉 All tests passed! System is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)