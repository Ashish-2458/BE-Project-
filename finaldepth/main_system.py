"""
Main Enhanced Vision Assistant System
Integrates camera, YOLO detection, depth estimation, LLM, and spatial audio
"""
import cv2
import time
import threading
from camera_system import CameraSystem
from yolo_detector import YOLODetector
from depth_estimator import DepthEstimator
from fusion_module import FusionModule
from llm_integration import LLMIntegration
from simple_audio_system import SimpleAudioSystem
from advanced_visualizer import AdvancedVisualizer

class EnhancedVisionAssistant:
    def __init__(self):
        # Initialize all components
        self.camera = CameraSystem()
        self.yolo = YOLODetector()
        self.depth_estimator = DepthEstimator()
        self.fusion = FusionModule()
        self.llm = LLMIntegration()
        self.audio = SimpleAudioSystem()
        self.visualizer = AdvancedVisualizer()
        
        # System state
        self.running = False
        self.processing_thread = None
        self.last_description_time = 0
        self.description_interval = 4.0  # Match API rate limit (4 seconds)
        self.last_immediate_warning = 0
        self.immediate_warning_cooldown = 1.0  # 1 second cooldown for immediate warnings
        
        # Display settings
        self.show_display = True
        self.display_depth = True
        self.advanced_mode = True  # Use advanced visualization
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
    def initialize(self):
        """Initialize all system components"""
        print("🚀 Initializing Enhanced Vision Assistant...")
        
        # Initialize components in order
        if not self.camera.start():
            print("❌ Failed to initialize camera")
            return False
            
        if not self.yolo.initialize():
            print("❌ Failed to initialize YOLO detector")
            return False
            
        if not self.depth_estimator.initialize():
            print("⚠️  Depth estimator using fallback mode (simple depth estimation)")
            # Continue anyway - we have fallback depth estimation
            
        if not self.audio.initialize():
            print("⚠️ Simple audio system failed, trying fallback...")
            # Try fallback to original audio system
            try:
                from audio_system import AudioSystem
                self.audio = AudioSystem()
                if not self.audio.initialize():
                    print("❌ Both audio systems failed")
                    return False
                else:
                    print("✅ Fallback audio system initialized")
            except Exception as e:
                print(f"❌ Fallback audio system error: {e}")
                return False
        
        print("✅ All systems initialized successfully!")
        return True
    
    def start(self):
        """Start the main processing loop"""
        if not self.initialize():
            return False
            
        self.running = True
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self._processing_loop)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        # Start display loop in main thread
        self._display_loop()
        
        return True
    
    def _processing_loop(self):
        """Main processing loop for detection and analysis"""
        print("🔄 Starting processing loop...")
        
        while self.running:
            try:
                # Get current frame
                frame = self.camera.get_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Parallel processing
                start_time = time.time()
                
                # YOLO Detection
                detections = self.yolo.detect_objects(frame)
                
                # Depth Estimation
                depth_map = self.depth_estimator.estimate_depth(frame)
                
                # Fusion - combine detection + depth
                enhanced_detections = self.fusion.fuse_detection_depth(
                    detections, depth_map, self.depth_estimator
                )
                
                # Generate navigation summary
                nav_summary = self.fusion.get_navigation_summary(enhanced_detections)
                
                # Process audio feedback
                self._process_audio_feedback(nav_summary, enhanced_detections)
                
                # Store results for display
                self.current_frame = frame
                self.current_detections = enhanced_detections
                self.current_depth = depth_map
                
                # Update FPS counter
                self._update_fps()
                
                processing_time = time.time() - start_time
                print(f"⚡ Processing time: {processing_time:.3f}s | Objects: {len(detections)} | Priority: {nav_summary['priority_objects']}")
                
                # Control processing rate
                time.sleep(max(0, 0.1 - processing_time))
                
            except Exception as e:
                print(f"❌ Error in processing loop: {e}")
                time.sleep(1)
    
    def _process_audio_feedback(self, nav_summary, enhanced_detections):
        """Enhanced audio feedback with smart timing"""
        current_time = time.time()
        
        # Check for immediate threats (high priority)
        immediate_objects = [
            det for det in enhanced_detections 
            if det.get('distance_zone') == 'immediate' and det.get('priority', False)
        ]
        
        # Check for close objects (medium priority)
        close_objects = [
            det for det in enhanced_detections 
            if det.get('distance_zone') == 'close' and det.get('priority', False)
        ]
        
        if immediate_objects and (current_time - self.last_immediate_warning) >= self.immediate_warning_cooldown:
            # Immediate warning with higher frequency
            obj = immediate_objects[0]
            warning = f"IMMEDIATE: {obj['class']} {obj['distance']} meters {obj['location_description']}"
            self.audio.speak_immediate_warning(warning)
            self.last_immediate_warning = current_time
            self.last_description_time = current_time
            
        elif close_objects and (current_time - self.last_description_time) >= (self.description_interval * 0.5):
            # Close objects get more frequent updates
            obj = close_objects[0]
            warning = f"CLOSE: {obj['class']} {obj['distance']} meters {obj['location_description']}"
            self.audio.speak_navigation_update(warning)
            self.last_description_time = current_time
            
        elif current_time - self.last_description_time >= self.description_interval:
            # Regular navigation update
            if nav_summary['priority_objects'] > 0:
                # Generate LLM description
                description = self.llm.generate_spatial_description(nav_summary)
                if description:
                    self.audio.speak_navigation_update(description)
                else:
                    # Fallback if LLM fails
                    top_obj = nav_summary['top_objects'][0] if nav_summary['top_objects'] else None
                    if top_obj:
                        fallback = f"{top_obj['class']} {top_obj.get('distance', 'unknown')} meters {top_obj.get('location_description', 'ahead')}"
                        self.audio.speak_navigation_update(fallback)
            else:
                # No priority objects
                self.audio.speak_scene_description("Path clear, no immediate obstacles")
            
            self.last_description_time = current_time
        
        # Debug: Print queue status occasionally
        if int(current_time) % 5 == 0:  # Every 5 seconds
            status = self.audio.get_queue_status()
            print(f"🎤 Audio Status: Queue={status['queue_size']}, Speaking={status['is_speaking']}")
    
    def _display_loop(self):
        """Display loop for visual feedback"""
        print("🖥️  Starting display loop...")
        
        while self.running:
            try:
                if hasattr(self, 'current_frame') and self.current_frame is not None:
                    
                    if self.advanced_mode:
                        # Use advanced visualization
                        if hasattr(self, 'current_depth') and self.current_depth is not None:
                            # Create enhanced depth view
                            display_frame = self.visualizer.create_enhanced_depth_view(
                                self.current_frame, self.current_depth, 
                                getattr(self, 'current_detections', [])
                            )
                        else:
                            display_frame = self.current_frame.copy()
                            if hasattr(self, 'current_detections'):
                                display_frame = self.visualizer._draw_enhanced_detections(
                                    display_frame, self.current_detections, None
                                )
                        
                        # Add enhanced UI
                        system_info = {
                            'objects': len(getattr(self, 'current_detections', [])),
                            'speaking': self.audio.is_currently_speaking(),
                            'fps': self.fps_counter
                        }
                        display_frame = self.visualizer.add_enhanced_ui(display_frame, system_info)
                        
                    else:
                        # Use original visualization
                        display_frame = self.current_frame.copy()
                        
                        # Draw detections
                        if hasattr(self, 'current_detections'):
                            display_frame = self._draw_enhanced_detections(
                                display_frame, self.current_detections
                            )
                        
                        # Show depth if enabled
                        if self.display_depth and hasattr(self, 'current_depth') and self.current_depth is not None:
                            depth_vis = self.depth_estimator.visualize_depth(self.current_depth)
                            if depth_vis is not None:
                                # Resize depth to match frame
                                depth_vis = cv2.resize(depth_vis, (display_frame.shape[1], display_frame.shape[0]))
                                # Combine side by side
                                display_frame = cv2.hconcat([display_frame, depth_vis])
                        
                        # Add system info
                        self._add_system_info(display_frame)
                    
                    # Display
                    cv2.imshow('Enhanced Vision Assistant', display_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.stop()
                    break
                elif key == ord('d'):
                    self.display_depth = not self.display_depth
                elif key == ord('s'):
                    self.audio.stop_speaking()
                elif key == ord('c'):
                    self.audio.clear_queue()
                elif key == ord('m'):
                    self.advanced_mode = not self.advanced_mode
                    mode = "Advanced" if self.advanced_mode else "Basic"
                    print(f"🎨 Switched to {mode} visualization mode")
                elif key == ord('t'):
                    # Test speech system
                    self.audio.force_speak("Testing speech system - this is a test message")
                    print("🧪 Testing speech system")
                elif key == ord('r'):
                    # Reset speech system
                    self.audio.stop_speaking()
                    self.audio.clear_queue()
                    try:
                        # Try to reinitialize
                        if hasattr(self.audio, '_reinitialize_engine'):
                            self.audio._reinitialize_engine()
                        else:
                            # For simple audio system, just clear and restart
                            self.audio.shutdown()
                            self.audio.initialize()
                    except Exception as e:
                        print(f"❌ Reset error: {e}")
                    print("🔄 Speech system reset")
                
            except Exception as e:
                print(f"❌ Error in display loop: {e}")
                time.sleep(0.1)
    
    def _draw_enhanced_detections(self, frame, detections):
        """Draw enhanced detection information"""
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            class_name = detection['class']
            confidence = detection['confidence']
            distance = detection.get('distance', 'N/A')
            priority = detection.get('navigation_priority', 0)
            
            # Color based on distance zone
            zone = detection.get('distance_zone', 'unknown')
            if zone == 'immediate':
                color = (0, 0, 255)  # Red
            elif zone == 'close':
                color = (0, 165, 255)  # Orange
            elif zone == 'medium':
                color = (0, 255, 255)  # Yellow
            else:
                color = (0, 255, 0)  # Green
            
            # Draw bounding box
            thickness = 3 if priority > 75 else 2
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
            
            # Create label with distance info
            if isinstance(distance, (int, float)):
                label = f"{class_name}: {distance}m"
            else:
                label = f"{class_name}: {confidence:.2f}"
            
            # Draw label background
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(frame, (x1, y1-25), (x1 + label_size[0], y1), color, -1)
            
            # Draw label text
            cv2.putText(frame, label, (x1, y1-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Draw priority indicator
            if priority > 50:
                cv2.circle(frame, (x2-10, y1+10), 5, (0, 0, 255), -1)
        
        return frame
    
    def _add_system_info(self, frame):
        """Add system information overlay"""
        h, w = frame.shape[:2]
        
        # System status
        status_text = f"Objects: {len(getattr(self, 'current_detections', []))}"
        cv2.putText(frame, status_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Audio status
        audio_status = "Speaking" if self.audio.is_currently_speaking() else "Ready"
        cv2.putText(frame, f"Audio: {audio_status}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Controls
        controls = "Q:Quit | D:Toggle Depth | S:Stop Speech | C:Clear Queue"
        cv2.putText(frame, controls, (10, h-20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def stop(self):
        """Stop the system gracefully"""
        print("🛑 Stopping Enhanced Vision Assistant...")
        
        self.running = False
        
        # Stop processing thread with timeout
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)
        
        # Stop components
        try:
            self.camera.stop()
        except Exception as e:
            print(f"Camera stop warning: {e}")
        
        try:
            self.audio.shutdown()
        except Exception as e:
            print(f"Audio stop warning: {e}")
        
        # Close windows
        try:
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"Window close warning: {e}")
        
        print("✅ System stopped successfully")
    
    def _update_fps(self):
        """Update FPS counter"""
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:  # Update every second
            self.fps_counter = 1.0 / max(0.001, current_time - self.last_fps_time)
            self.last_fps_time = current_time

def main():
    """Main entry point"""
    assistant = EnhancedVisionAssistant()
    
    try:
        assistant.start()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ System error: {e}")
    finally:
        assistant.stop()

if __name__ == "__main__":
    main()