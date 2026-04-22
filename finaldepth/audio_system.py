"""
Enhanced Spatial Audio TTS System with Smart Queue Management
"""
import pyttsx3
import threading
import time
from collections import deque
from config import TTS_RATE, TTS_VOLUME

class AudioSystem:
    def __init__(self):
        self.engine = None
        self.is_speaking = False
        self.speech_queue = deque(maxlen=10)  # Use deque for better performance
        self.speech_thread = None
        self.running = False
        self.queue_lock = threading.Lock()
        self.last_speech_time = 0
        self.min_speech_interval = 1.0  # Minimum 1 second between speeches
        self.max_queue_size = 3  # Smart queue limit
        
    def initialize(self):
        """Initialize TTS engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Configure TTS settings
            self.engine.setProperty('rate', TTS_RATE)
            self.engine.setProperty('volume', TTS_VOLUME)
            
            # Try to set a clear voice
            voices = self.engine.getProperty('voices')
            if voices:
                # Prefer female voice if available (often clearer)
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                else:
                    # Use first available voice
                    self.engine.setProperty('voice', voices[0].id)
            
            # Start speech processing thread
            self.running = True
            self.speech_thread = threading.Thread(target=self._speech_worker)
            self.speech_thread.daemon = True
            self.speech_thread.start()
            
            print("Audio system initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing audio system: {e}")
            return False
    
    def speak_navigation(self, text, priority='normal'):
        """
        Enhanced speech queue with smart management
        Args:
            text: Text to speak
            priority: 'urgent', 'normal', 'low'
        """
        if not self.engine or not text:
            return
            
        current_time = time.time()
        
        # Rate limiting - don't spam speech
        if priority != 'urgent' and (current_time - self.last_speech_time) < self.min_speech_interval:
            return
            
        speech_item = {
            'text': text,
            'priority': priority,
            'timestamp': current_time,
            'id': f"{priority}_{current_time}"
        }
        
        with self.queue_lock:
            # Smart queue management
            if priority == 'urgent':
                # Clear everything for urgent messages
                self.speech_queue.clear()
                self.speech_queue.appendleft(speech_item)
                # Interrupt current speech
                if self.is_speaking:
                    try:
                        self.engine.stop()
                    except:
                        pass
                    
            elif priority == 'normal':
                # Smart queue limit management
                if len(self.speech_queue) >= self.max_queue_size:
                    # Keep only 2 most recent items, add new one
                    recent_items = list(self.speech_queue)[-2:]
                    self.speech_queue.clear()
                    self.speech_queue.extend(recent_items)
                
                self.speech_queue.append(speech_item)
                
            else:  # low priority
                # Only add if queue has space
                if len(self.speech_queue) < 2:
                    self.speech_queue.append(speech_item)
        
        print(f"🔊 Queued [{priority}]: {text[:50]}... | Queue size: {len(self.speech_queue)}")
    
    def _speech_worker(self):
        """Enhanced background thread for processing speech queue"""
        while self.running:
            try:
                speech_item = None
                
                # Get next item from queue
                with self.queue_lock:
                    if self.speech_queue and not self.is_speaking:
                        speech_item = self.speech_queue.popleft()
                
                if speech_item:
                    # Check if item is still relevant (not too old)
                    age = time.time() - speech_item['timestamp']
                    if age < 10.0:  # Discard items older than 10 seconds
                        self._speak_text(speech_item['text'], speech_item['priority'])
                        self.last_speech_time = time.time()
                    else:
                        print(f"🗑️ Discarded old speech: {speech_item['text'][:30]}...")
                
                time.sleep(0.05)  # Faster polling
                
            except Exception as e:
                print(f"❌ Speech worker error: {e}")
                time.sleep(0.5)
    
    def _speak_text(self, text, priority='normal'):
        """Enhanced text-to-speech with better error handling"""
        try:
            self.is_speaking = True
            print(f"🔊 Speaking [{priority}]: {text}")
            
            # Add spatial audio cues based on content
            enhanced_text = self._add_spatial_cues(text)
            
            # Ensure engine is ready
            if not self.engine:
                print("❌ TTS engine not available")
                return
                
            # Clear any pending speech first
            try:
                self.engine.stop()
            except:
                pass
            
            # Speak with timeout protection
            self.engine.say(enhanced_text)
            
            # Use runAndWait with timeout protection
            start_time = time.time()
            self.engine.runAndWait()
            
            # Log speech duration
            duration = time.time() - start_time
            print(f"✅ Speech completed in {duration:.1f}s")
            
        except Exception as e:
            print(f"❌ Speech synthesis error: {e}")
            # Try to reinitialize engine if it failed
            try:
                self._reinitialize_engine()
            except:
                pass
        finally:
            self.is_speaking = False
    
    def _reinitialize_engine(self):
        """Reinitialize TTS engine if it fails"""
        try:
            if self.engine:
                del self.engine
            
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', TTS_RATE)
            self.engine.setProperty('volume', TTS_VOLUME)
            
            # Set voice
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id)
            
            print("🔄 TTS engine reinitialized")
            
        except Exception as e:
            print(f"❌ Failed to reinitialize TTS engine: {e}")
    
    def _add_spatial_cues(self, text):
        """Add spatial audio cues to text"""
        # Add pauses and emphasis for better spatial understanding
        enhanced = text
        
        # Add pauses after direction words
        direction_words = ['left', 'right', 'center', 'ahead', 'behind']
        for word in direction_words:
            enhanced = enhanced.replace(word, f"{word}...")
        
        # Add emphasis to distance information
        distance_phrases = ['meters', 'close', 'far', 'immediate']
        for phrase in distance_phrases:
            enhanced = enhanced.replace(phrase, f"*{phrase}*")
        
        # Add urgency markers
        urgent_words = ['blocking', 'obstacle', 'immediate', 'danger']
        for word in urgent_words:
            if word in enhanced.lower():
                enhanced = f"ATTENTION: {enhanced}"
                break
        
        return enhanced
    
    def speak_immediate_warning(self, text):
        """Speak urgent warning immediately"""
        self.speak_navigation(text, priority='urgent')
    
    def speak_scene_description(self, text):
        """Speak general scene description"""
        self.speak_navigation(text, priority='low')
    
    def speak_navigation_update(self, text):
        """Speak navigation update"""
        self.speak_navigation(text, priority='normal')
    
    def is_currently_speaking(self):
        """Check if currently speaking"""
        return self.is_speaking
    
    def clear_queue(self):
        """Clear speech queue with thread safety"""
        with self.queue_lock:
            self.speech_queue.clear()
        print("🗑️ Speech queue cleared")
    
    def stop_speaking(self):
        """Stop current speech immediately"""
        try:
            if self.engine and self.is_speaking:
                self.engine.stop()
                print("🛑 Speech stopped")
        except Exception as e:
            print(f"❌ Error stopping speech: {e}")
    
    def get_queue_status(self):
        """Get current queue status"""
        with self.queue_lock:
            return {
                'queue_size': len(self.speech_queue),
                'is_speaking': self.is_speaking,
                'items': [item['text'][:30] + '...' for item in list(self.speech_queue)[:3]]
            }
    
    def force_speak(self, text):
        """Force immediate speech, bypassing queue"""
        if not self.running:
            return
            
        # Stop everything and speak immediately
        self.stop_speaking()
        self.clear_queue()
        
        # Speak directly
        threading.Thread(target=self._speak_text, args=(text, 'urgent'), daemon=True).start()
    
    def shutdown(self):
        """Shutdown audio system"""
        self.running = False
        self.clear_queue()
        self.stop_speaking()
        
        if self.speech_thread:
            self.speech_thread.join(timeout=2)
        
        print("Audio system shutdown")