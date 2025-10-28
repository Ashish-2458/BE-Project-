#!/usr/bin/env python3
"""
AI-Powered Assistive Vision System
Real-time object detection with natural language scene description for visually impaired users
"""

import cv2
import time
import signal
import sys
from typing import List, Dict, Optional
import threading

from modules.camera import CameraCapture
from modules.detector import ObjectDetector
from modules.llm_client import GeminiClient
from modules.speech import TextToSpeech
import config

class AssistiveVisionSystem:
    """Main application class that orchestrates all components"""
    
    def __init__(self):
        self.camera = None
        self.detector = None
        self.llm_client = None
        self.tts = None
        self.running = False
        
        # State tracking
        self.last_detection_time = 0
        self.last_description_time = 0
        self.last_quick_speech_time = 0
        self.previous_objects = set()
        self.current_detections = []
        self.speech_counter = 0
        
        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()
        
    def initialize(self) -> bool:
        """Initialize all system components"""
        print("🚀 Initializing Assistive Vision System...")
        
        try:
            # Initialize camera
            print("📷 Starting camera...")
            self.camera = CameraCapture(
                camera_index=config.CAMERA_INDEX,
                width=config.FRAME_WIDTH,
                height=config.FRAME_HEIGHT
            )
            if not self.camera.start():
                print("❌ Failed to start camera")
                return False
            
            # Initialize object detector
            print("🔍 Loading YOLO model...")
            self.detector = ObjectDetector(
                model_path=config.YOLO_MODEL,
                confidence=config.CONFIDENCE_THRESHOLD
            )
            
            # Initialize LLM client
            print("🧠 Connecting to Gemini API...")
            self.llm_client = GeminiClient(
                api_key=config.GEMINI_API_KEY,
                api_url=config.GEMINI_API_URL
            )
            
            # Initialize text-to-speech
            print("🔊 Starting text-to-speech...")
            self.tts = TextToSpeech(
                rate=config.SPEECH_RATE,
                volume=config.SPEECH_VOLUME
            )
            
            print("✅ All systems initialized successfully!")
            
            # Welcome message
            self.tts.speak_immediate(
                "Assistive vision system is now active. I'll help you navigate your surroundings."
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            return False
    
    def process_frame(self, frame) -> Optional[List[Dict]]:
        """Process a single frame and return detections"""
        current_time = time.time()
        
        # Rate limiting for detection
        if current_time - self.last_detection_time < config.DETECTION_INTERVAL:
            return self.current_detections
        
        # Run object detection
        detections = self.detector.detect_objects(frame)
        self.current_detections = detections
        self.last_detection_time = current_time
        
        return detections
    
    def analyze_scene_changes(self, detections: List[Dict]) -> bool:
        """Determine if scene has changed significantly"""
        current_objects = set()
        
        for detection in detections:
            # Include distance in the key for more sensitive change detection
            obj_key = f"{detection['class_name']}_{detection['position']}_{detection['distance']}"
            current_objects.add(obj_key)
        
        # Calculate change ratio
        if not self.previous_objects:
            change_ratio = 1.0
        else:
            intersection = len(current_objects.intersection(self.previous_objects))
            union = len(current_objects.union(self.previous_objects))
            change_ratio = 1.0 - (intersection / union if union > 0 else 0)
        
        significant_change = (
            change_ratio > 0.1 or  # 10% change in objects (very sensitive)
            len(current_objects) != len(self.previous_objects) or
            time.time() - self.last_description_time > 6.0  # Force full update every 6 seconds
        )
        
        if significant_change:
            self.previous_objects = current_objects.copy()
        
        return significant_change
    
    def generate_audio_feedback(self, detections: List[Dict]):
        """Generate appropriate audio feedback based on detections"""
        current_time = time.time()
        
        # Force speech every 4 seconds with quick descriptions
        time_since_last_speech = current_time - self.last_quick_speech_time
        
        if time_since_last_speech >= 4.0:  # Every 4 seconds guaranteed
            if detections:
                # Use quick description for frequent updates
                quick_desc = self.llm_client.get_quick_description(detections)
                self.tts.speak(quick_desc)
                self.last_quick_speech_time = current_time
                print(f"🗣️  Quick: {quick_desc}")
            else:
                self.tts.speak("Path clear.")
                self.last_quick_speech_time = current_time
                print("🗣️  Quick: Path clear.")
        
        # Generate detailed scene description if scene changed significantly
        elif self.analyze_scene_changes(detections):
            # Every 3rd speech should be detailed (using API)
            self.speech_counter += 1
            if self.speech_counter % 3 == 0:
                try:
                    description = self.llm_client.describe_scene(detections)
                    if description:
                        self.tts.speak(description)
                        self.last_description_time = current_time
                        self.last_quick_speech_time = current_time  # Reset quick speech timer
                        print(f"🗣️  Detailed: {description}")
                except Exception as e:
                    # Fallback to quick description if API fails
                    quick_desc = self.llm_client.get_quick_description(detections)
                    self.tts.speak(quick_desc)
                    self.last_quick_speech_time = current_time
                    print(f"🗣️  Fallback: {quick_desc}")
            else:
                # Use quick description for immediate feedback
                quick_desc = self.llm_client.get_quick_description(detections)
                self.tts.speak(quick_desc)
                self.last_quick_speech_time = current_time
                print(f"🗣️  Quick: {quick_desc}")
    
    def run_visual_mode(self):
        """Run with visual display (for development/testing)"""
        print("👁️  Starting visual mode (press 'q' to quit, 's' for status)")
        
        # Initialize window
        cv2.namedWindow('Assistive Vision System', cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow('Assistive Vision System', 100, 100)
        
        while self.running:
            frame = self.camera.get_frame()
            if frame is None:
                continue
            
            # Process frame
            detections = self.process_frame(frame)
            
            # ALWAYS generate audio feedback (critical for blind users)
            try:
                self.generate_audio_feedback(detections)
            except Exception as e:
                print(f"❌ Audio feedback error: {e}")
            
            # Visual display
            try:
                if detections:
                    # Draw detections on frame
                    annotated_frame = self.detector.draw_detections(frame, detections)
                    
                    # Add system info
                    fps = self.frame_count / (time.time() - self.start_time) if time.time() > self.start_time else 0
                    info_text = f"Objects: {len(detections)} | FPS: {fps:.1f} | Speaking: {self.tts.is_busy()}"
                    cv2.putText(annotated_frame, info_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    
                    # Add instructions
                    cv2.putText(annotated_frame, "Press 'q' to quit, 's' for status", (10, frame.shape[0] - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    cv2.imshow('Assistive Vision System', annotated_frame)
                else:
                    # Add info to clean frame
                    display_frame = frame.copy()
                    fps = self.frame_count / (time.time() - self.start_time) if time.time() > self.start_time else 0
                    info_text = f"No objects detected | FPS: {fps:.1f} | Speaking: {self.tts.is_busy()}"
                    cv2.putText(display_frame, info_text, (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(display_frame, "Press 'q' to quit, 's' for status", (10, frame.shape[0] - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    cv2.imshow('Assistive Vision System', display_frame)
                
                # Make sure window is visible
                cv2.setWindowProperty('Assistive Vision System', cv2.WND_PROP_TOPMOST, 1)
                
            except Exception as e:
                print(f"❌ Display error: {e}")
                # Fallback: just show the raw frame
                cv2.imshow('Assistive Vision System', frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self.print_status()
            
            self.frame_count += 1
        
        cv2.destroyAllWindows()
    
    def run_headless_mode(self):
        """Run without visual display (production mode)"""
        print("🎧 Starting headless mode (Ctrl+C to quit)")
        
        while self.running:
            frame = self.camera.get_frame()
            if frame is None:
                time.sleep(0.1)
                continue
            
            # Process frame
            detections = self.process_frame(frame)
            
            if detections:
                # Generate audio feedback
                self.generate_audio_feedback(detections)
            
            self.frame_count += 1
            time.sleep(0.1)  # Small delay to prevent excessive CPU usage
    
    def print_status(self):
        """Print current system status"""
        fps = self.frame_count / (time.time() - self.start_time) if time.time() > self.start_time else 0
        print(f"\n📊 System Status:")
        print(f"   Camera: {'✅ Active' if self.camera.is_running() else '❌ Inactive'}")
        print(f"   FPS: {fps:.1f}")
        print(f"   Objects detected: {len(self.current_detections)}")
        print(f"   Speech queue: {'🔊 Speaking' if self.tts.is_busy() else '🔇 Idle'}")
        print(f"   Runtime: {time.time() - self.start_time:.1f}s")
    
    def shutdown(self):
        """Gracefully shutdown all components"""
        print("\n🛑 Shutting down system...")
        self.running = False
        
        if self.tts:
            self.tts.speak_immediate("System shutting down. Goodbye.")
            time.sleep(2)  # Allow final message to play
            self.tts.shutdown()
        
        if self.camera:
            self.camera.stop()
        
        print("✅ Shutdown complete")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Received interrupt signal...")
    if 'system' in globals():
        system.shutdown()
    sys.exit(0)

def main():
    """Main entry point"""
    global system
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and initialize system
    system = AssistiveVisionSystem()
    
    if not system.initialize():
        print("❌ Failed to initialize system")
        return 1
    
    system.running = True
    
    try:
        # Choose mode based on environment
        import os
        if os.environ.get('DISPLAY') or sys.platform == 'win32':
            # Visual mode if display available
            print("👁️ Starting visual mode (press 'q' to quit, 's' for status)")
            system.run_visual_mode()
        else:
            # Headless mode for production
            print("🎧 Running in headless mode (audio-only)")
            system.run_headless_mode()
            
    except KeyboardInterrupt:
        pass
    finally:
        system.shutdown()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)