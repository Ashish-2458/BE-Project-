"""
Test script for Enhanced Vision Assistant components
"""
import cv2
import numpy as np
from camera_system import CameraSystem
from yolo_detector import YOLODetector
from depth_estimator import DepthEstimator

def test_camera():
    """Test camera system"""
    print("🧪 Testing Camera System...")
    camera = CameraSystem()
    
    if camera.start():
        print("✅ Camera started successfully")
        
        # Get a few frames
        for i in range(5):
            frame = camera.get_frame()
            if frame is not None:
                print(f"✅ Frame {i+1}: {frame.shape}")
            else:
                print(f"❌ Frame {i+1}: None")
        
        camera.stop()
        return True
    else:
        print("❌ Camera failed to start")
        return False

def test_yolo():
    """Test YOLO detector"""
    print("\n🧪 Testing YOLO Detector...")
    detector = YOLODetector()
    
    if detector.initialize():
        print("✅ YOLO initialized successfully")
        
        # Test with a dummy frame
        dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector.detect_objects(dummy_frame)
        print(f"✅ YOLO detection test: {len(detections)} objects")
        return True
    else:
        print("❌ YOLO failed to initialize")
        return False

def test_depth():
    """Test depth estimator"""
    print("\n🧪 Testing Depth Estimator...")
    estimator = DepthEstimator()
    
    # This will try the models and fall back to simple estimation
    estimator.initialize()
    print("✅ Depth estimator initialized (may be using fallback)")
    
    # Test with a dummy frame
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    depth_map = estimator.estimate_depth(dummy_frame)
    
    if depth_map is not None:
        print(f"✅ Depth estimation test: {depth_map.shape}")
        return True
    else:
        print("❌ Depth estimation failed")
        return False

def test_integration():
    """Test basic integration"""
    print("\n🧪 Testing System Integration...")
    
    camera = CameraSystem()
    yolo = YOLODetector()
    depth = DepthEstimator()
    
    # Initialize components
    camera_ok = camera.start()
    yolo_ok = yolo.initialize()
    depth_ok = depth.initialize()
    
    if camera_ok and yolo_ok:
        print("✅ Core components initialized")
        
        # Get a real frame and process it
        frame = camera.get_frame()
        if frame is not None:
            print(f"✅ Got frame: {frame.shape}")
            
            # Test detection
            detections = yolo.detect_objects(frame)
            print(f"✅ Detected {len(detections)} objects")
            
            # Test depth
            depth_map = depth.estimate_depth(frame)
            if depth_map is not None:
                print(f"✅ Generated depth map: {depth_map.shape}")
            
            # Test distance calculation
            if detections and depth_map is not None:
                for det in detections[:3]:  # Test first 3 detections
                    distance = depth.get_object_distance(depth_map, det['center'], det['bbox'])
                    print(f"✅ Object '{det['class']}' distance: {distance}m")
        
        camera.stop()
        return True
    else:
        print("❌ Integration test failed")
        if camera_ok:
            camera.stop()
        return False

def main():
    """Run all tests"""
    print("🚀 Enhanced Vision Assistant - Component Tests\n")
    
    results = []
    
    # Run individual tests
    results.append(("Camera", test_camera()))
    results.append(("YOLO", test_yolo()))
    results.append(("Depth", test_depth()))
    results.append(("Integration", test_integration()))
    
    # Print results
    print("\n📊 Test Results:")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:12} : {status}")
        if result:
            passed += 1
    
    print("=" * 40)
    print(f"Tests Passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 All tests passed! System ready to run.")
        print("Run: python main_system.py")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Check the errors above.")

if __name__ == "__main__":
    main()