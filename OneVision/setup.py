#!/usr/bin/env python3
"""
Setup script for Assistive Vision System
Installs dependencies and performs initial setup
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Assistive Vision System...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return 1
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("💡 Try: python -m pip install --upgrade pip")
        print("💡 Or: pip install --user -r requirements.txt")
        return 1
    
    # Download YOLO model
    print("📥 Downloading YOLO model (this may take a moment)...")
    try:
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')  # This will download the model
        print("✅ YOLO model downloaded successfully")
    except Exception as e:
        print(f"⚠️  YOLO model download failed: {e}")
        print("💡 The model will be downloaded automatically on first run")
    
    # Test camera access
    print("📷 Testing camera access...")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✅ Camera test successful")
            else:
                print("⚠️  Camera opened but couldn't read frame")
            cap.release()
        else:
            print("⚠️  Could not open camera - check if camera is connected and not in use")
    except Exception as e:
        print(f"⚠️  Camera test failed: {e}")
    
    # Test text-to-speech
    print("🔊 Testing text-to-speech...")
    try:
        import pyttsx3
        engine = pyttsx3.init()
        print("✅ Text-to-speech initialized successfully")
    except Exception as e:
        print(f"⚠️  Text-to-speech test failed: {e}")
        print("💡 On Linux, you may need: sudo apt-get install espeak espeak-data libespeak1 libespeak-dev")
        print("💡 On macOS, text-to-speech should work out of the box")
    
    print("\n🎉 Setup complete!")
    print("\n🚀 To run the system:")
    print("   python main.py")
    print("\n💡 Tips:")
    print("   - Press 'q' to quit in visual mode")
    print("   - Press 's' for system status")
    print("   - Use Ctrl+C to stop in headless mode")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)