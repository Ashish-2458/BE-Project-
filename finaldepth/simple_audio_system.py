"""
Simple and Reliable Audio System for Navigation Assistance
"""
import threading
import time
import os
import tempfile
from collections import deque
from config import TTS_RATE, TTS_VOLUME

class SimpleAudioSystem:
    def __init__(self):
        self.is_speaking = False
        self.speech_queue = deque(maxlen=5)
        self.speech_thread = None
        self.running = False
        self.queue_lock = threading.Lock()
        self.last_speech_time = 0
        self.min_speech_interval = 1.2  # Comfortable interval between speeches
        
    def initialize(self):
        """Initialize simple audio system"""
        try:
            # Test Windows SAPI
            self._test_sapi()
            
            # Start speech processing thread
            self.running = True
            self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
            self.speech_thread.start()
            
            print("✅ Simple audio system initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing audio system: {e}")
            return False
    
    def _test_sapi(self):
        """Test Windows SAPI availability"""
        try:
            # Test basic SAPI command
            os.system('echo "Audio test" | clip')
            print("🔊 Windows SAPI available")
        except Exception as e:
            print(f"⚠️ SAPI test warning: {e}")
    
    def speak_navigation(self, text, priority='normal'):
        """Add text to speech queue"""
        if not text or not self.running:
            return
            
        current_time = time.time()
        
        # Rate limiting
        if priority != 'urgent' and (current_time - self.last_speech_time) < self.min_speech_interval:
            print(f"⏳ Rate limited: {text[:30]}...")
            return
            
        speech_item = {
            'text': text,
            'priority': priority,
            'timestamp': current_time
        }
        
        with self.queue_lock:
            # Handle different priorities
            if priority == 'urgent':
                # Clear queue and add urgent message at front
                self.speech_queue.clear()
                self.speech_queue.appendleft(speech_item)
                print(f"🚨 URGENT queued: {text[:50]}...")
            else:
                # Add to queue, limit size
                if len(self.speech_queue) >= 3:
                    # Remove oldest item
                    old_item = self.speech_queue.popleft()
                    print(f"🗑️ Removed old: {old_item['text'][:30]}...")
                
                self.speech_queue.append(speech_item)
                print(f"🔊 Queued [{priority}]: {text[:50]}... | Queue: {len(self.speech_queue)}")
    
    def _speech_worker(self):
        """Background thread for processing speech"""
        print("🎤 Speech worker started")
        
        while self.running:
            try:
                speech_item = None
                
                # Get next item from queue
                with self.queue_lock:
                    if self.speech_queue and not self.is_speaking:
                        speech_item = self.speech_queue.popleft()
                
                if speech_item:
                    # Check if item is still fresh
                    age = time.time() - speech_item['timestamp']
                    if age < 15.0:  # Discard items older than 15 seconds
                        self._speak_with_sapi(speech_item['text'], speech_item['priority'])
                        self.last_speech_time = time.time()
                    else:
                        print(f"🗑️ Discarded stale speech: {speech_item['text'][:30]}...")
                
                time.sleep(0.1)  # Check queue every 100ms
                
            except Exception as e:
                print(f"❌ Speech worker error: {e}")
                time.sleep(1)
                
        print("🎤 Speech worker stopped")
    
    def _speak_with_sapi(self, text, priority='normal'):
        """Speak using Windows SAPI with faster method"""
        try:
            self.is_speaking = True
            print(f"🔊 Speaking [{priority}]: {text}")
            
            # Clean text for SAPI
            clean_text = self._clean_text_for_sapi(text)
            
            # Use optimized PowerShell command with comfortable speech rate
            # SAPI Rate: -10 (slowest) to +10 (fastest), 0 is normal
            fast_rate = 4  # Fast but comfortable speech for navigation (reduced from 8)
            
            # Properly escape the text for PowerShell
            escaped_text = clean_text.replace("'", "''").replace('"', '""')
            ps_command = f"Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Rate = {fast_rate}; $s.Volume = 90; $s.Speak('{escaped_text}'); $s.Dispose()"
            
            try:
                # Execute PowerShell command directly
                start_time = time.time()
                result = os.system(f'powershell -Command "{ps_command}"')
                duration = time.time() - start_time
                
                if result == 0:
                    print(f"✅ Speech completed in {duration:.1f}s")
                else:
                    print(f"⚠️ Speech command returned code: {result}")
                    
            except Exception as cmd_error:
                print(f"❌ PowerShell error: {cmd_error}")
                # Try even simpler fallback
                try:
                    # Use msg command as last resort
                    os.system(f'echo {clean_text[:50]} | msg * /time:3')
                except:
                    # Final fallback - just print
                    print(f"📢 SPEECH: {clean_text}")
                    
        except Exception as e:
            print(f"❌ SAPI speech error: {e}")
            # Fallback to simple notification
            print(f"📢 SPEECH: {text}")
        finally:
            self.is_speaking = False
    
    def _clean_text_for_sapi(self, text):
        """Clean and optimize text for fast SAPI speech"""
        # Remove problematic characters
        clean = text.replace('"', "'").replace('`', "'").replace('$', 'dollars')
        
        # Make speech more concise for faster delivery
        clean = self._make_concise(clean)
        
        # Limit length for faster speech
        if len(clean) > 150:  # Shorter limit for faster speech
            clean = clean[:147] + "..."
            
        return clean
    
    def _make_concise(self, text):
        """Make text more concise but still natural"""
        # Replace only the most verbose phrases, keep it natural
        replacements = {
            "There's a person about": "Person",
            "Be aware, there's": "There's",
            "You can safely navigate": "Navigate",
            "straight ahead": "ahead",
            "in the center": "center",
            "Gently steer": "Steer",
            "Carefully navigate": "Navigate",
            "blocking your path": "blocking path",
            "approximately": "about",
        }
        
        result = text
        for old, new in replacements.items():
            result = result.replace(old, new)
        
        # Clean up extra spaces
        result = ' '.join(result.split())
        
        return result
    
    def speak_immediate_warning(self, text):
        """Speak urgent warning"""
        self.speak_navigation(f"ATTENTION: {text}", priority='urgent')
    
    def speak_navigation_update(self, text):
        """Speak navigation update"""
        self.speak_navigation(text, priority='normal')
    
    def speak_scene_description(self, text):
        """Speak scene description"""
        self.speak_navigation(text, priority='low')
    
    def is_currently_speaking(self):
        """Check if currently speaking"""
        return self.is_speaking
    
    def clear_queue(self):
        """Clear speech queue"""
        with self.queue_lock:
            cleared_count = len(self.speech_queue)
            self.speech_queue.clear()
        print(f"🗑️ Cleared {cleared_count} items from speech queue")
    
    def stop_speaking(self):
        """Stop current speech (limited capability with SAPI)"""
        print("🛑 Speech stop requested (SAPI has limited interrupt capability)")
        # SAPI doesn't have easy interrupt, but we can clear the queue
        self.clear_queue()
    
    def get_queue_status(self):
        """Get queue status"""
        with self.queue_lock:
            return {
                'queue_size': len(self.speech_queue),
                'is_speaking': self.is_speaking,
                'items': [item['text'][:30] + '...' for item in list(self.speech_queue)[:3]]
            }
    
    def force_speak(self, text):
        """Force immediate speech"""
        self.clear_queue()
        self.speak_immediate_warning(text)
    
    def shutdown(self):
        """Shutdown audio system"""
        print("🔇 Shutting down audio system...")
        self.running = False
        self.clear_queue()
        
        if self.speech_thread and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=3)
        
        print("✅ Audio system shutdown complete")