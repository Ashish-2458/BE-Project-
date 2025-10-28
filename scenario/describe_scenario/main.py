"""
Describe Scenario - Continuous AI-powered environmental descriptions
Main application for visually impaired users
"""
import time
import signal
import sys
import threading
from typing import Optional

from camera_handler import CameraHandler
from gemini_client import GeminiClient
from speech_engine import SpeechEngine
import config

class DescribeScenarioApp:
    """Main application for continuous environmental descriptions"""
    
    def __init__(self):
        self.camera = None
        self.ai_client = None
        self.speech = None
        self.running = False
        self.real_time_mode = False
        self.description_thread = None
        
    def initialize(self) -> bool:
        """Initialize all system components"""
        print("🚀 Initializing Describe Scenario System...")
        
        try:
            # Initialize speech engine first (for user feedback)
            print("🔊 Starting speech engine...")
            self.speech = SpeechEngine()
            
            # Initialize camera
            print("📷 Initializing camera...")
            self.camera = CameraHandler()
            if not self.camera.initialize():
                self.speech.speak_immediate("Camera initialization failed. Please check your camera connection.")
                return False
            
            # Initialize AI client
            print("🧠 Connecting to AI service...")
            self.ai_client = GeminiClient()
            
            # Test AI connection
            if not self.ai_client.test_connection():
                self.speech.speak_immediate("AI service connection failed. Please check your internet connection.")
                return False
            
            print("✅ All systems initialized successfully!")
            self.speech.speak_immediate("Describe scenario system is ready. I will now capture and describe your surroundings.")
            
            return True
            
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            if self.speech:
                self.speech.speak_immediate("System initialization failed. Please try again.")
            return False
    
    def capture_and_describe(self) -> bool:
        """Capture image and get AI description"""
        try:
            print("📸 Capturing image...")
            
            # Capture frame and encode
            image_base64 = self.camera.capture_and_encode()
            if not image_base64:
                print("❌ Failed to capture image")
                self.speech.speak("Failed to capture image. Trying again.")
                return False
            
            print("🧠 Getting AI description...")
            
            # Get AI description
            description = self.ai_client.describe_image(image_base64)
            if not description:
                print("❌ Failed to get AI description")
                self.speech.speak("AI description failed. Trying again in a moment.")
                return False
            
            # Speak the description
            print(f"📝 Description: {description}")
            self.speech.speak(description)
            
            return True
            
        except Exception as e:
            print(f"❌ Capture and describe error: {e}")
            self.speech.speak("An error occurred while describing the scene.")
            return False
    
    def real_time_loop(self):
        """Real-time description loop (runs in separate thread)"""
        print("🔄 Starting real-time mode...")
        self.speech.speak("Entering real-time mode. I will describe your surroundings every 10 seconds.")
        
        retry_count = 0
        max_retries = config.MAX_RETRIES
        
        while self.real_time_mode and self.running:
            try:
                success = self.capture_and_describe()
                
                if success:
                    retry_count = 0  # Reset retry counter on success
                else:
                    retry_count += 1
                    if retry_count >= max_retries:
                        self.speech.speak("Multiple failures detected. Exiting real-time mode.")
                        break
                
                # Wait for the interval (but check for stop signal)
                for _ in range(int(config.DESCRIPTION_INTERVAL * 10)):
                    if not self.real_time_mode or not self.running:
                        break
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"❌ Real-time loop error: {e}")
                retry_count += 1
                if retry_count >= max_retries:
                    self.speech.speak("Too many errors. Exiting real-time mode.")
                    break
                time.sleep(1)
        
        self.real_time_mode = False
        print("🛑 Real-time mode stopped")
    
    def start_real_time_mode(self):
        """Start real-time description mode"""
        if self.real_time_mode:
            print("⚠️ Real-time mode already active")
            return
            
        self.real_time_mode = True
        self.description_thread = threading.Thread(target=self.real_time_loop, daemon=True)
        self.description_thread.start()
    
    def stop_real_time_mode(self):
        """Stop real-time description mode"""
        if not self.real_time_mode:
            print("⚠️ Real-time mode not active")
            return
            
        print("🛑 Stopping real-time mode...")
        self.real_time_mode = False
        
        if self.description_thread:
            self.description_thread.join(timeout=2.0)
            
        self.speech.speak("Real-time mode stopped. Returning to main menu.")
    
    def run(self):
        """Main application loop"""
        if not self.initialize():
            return 1
            
        self.running = True
        
        try:
            # Initial description
            print("📸 Taking initial description...")
            success = self.capture_and_describe()
            
            if success:
                # Wait for initial description to complete
                self.speech.wait_until_done(timeout=15)
                
                # Start real-time mode
                self.start_real_time_mode()
                
                # Keep running until user stops
                print("\n" + "="*50)
                print("🎧 REAL-TIME MODE ACTIVE")
                print("Press Ctrl+C to stop and return to main menu")
                print("="*50 + "\n")
                
                while self.running and self.real_time_mode:
                    time.sleep(1)
                    
            else:
                self.speech.speak("Initial description failed. Please try again.")
                
        except KeyboardInterrupt:
            print("\n🛑 Stop signal received...")
            self.stop_real_time_mode()
            
        except Exception as e:
            print(f"❌ Application error: {e}")
            self.speech.speak("An unexpected error occurred.")
            
        finally:
            self.shutdown()
            
        return 0
    
    def shutdown(self):
        """Gracefully shutdown all components"""
        print("\n🛑 Shutting down system...")
        self.running = False
        self.real_time_mode = False
        
        if self.speech:
            self.speech.speak_immediate("System shutting down. Goodbye.")
            time.sleep(2)  # Allow final message
            self.speech.shutdown()
            
        if self.camera:
            self.camera.release()
            
        print("✅ Shutdown complete")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Received interrupt signal...")
    if 'app' in globals():
        app.shutdown()
    sys.exit(0)

def main():
    """Main entry point"""
    global app
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🎯 Describe Scenario - AI-Powered Environmental Descriptions")
    print("Designed for visually impaired users")
    print("-" * 60)
    
    # Create and run application
    app = DescribeScenarioApp()
    exit_code = app.run()
    
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)