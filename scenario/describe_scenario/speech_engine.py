"""
Text-to-speech engine for audio feedback
"""
import threading
import queue
import time
import sys
from typing import Optional
import config

class SpeechEngine:
    """Text-to-speech engine with smart queue management"""
    
    def __init__(self):
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.running = True
        self.use_sapi = False
        self.use_pyttsx3 = False
        self.max_queue_size = 2  # Keep only 2 latest descriptions
        
        # Initialize TTS engine
        self._initialize_engine()
        
        # Start speech worker thread
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
        
    def _initialize_engine(self):
        """Initialize the TTS engine - try multiple methods"""
        # Method 1: Try Windows SAPI (most reliable on Windows)
        if sys.platform == 'win32':
            try:
                import win32com.client
                self.sapi = win32com.client.Dispatch("SAPI.SpVoice")
                self.sapi.Rate = max(-2, min(2, (config.SPEECH_RATE - 150) // 25))
                self.sapi.Volume = int(config.SPEECH_VOLUME * 100)
                self.use_sapi = True
                print("✅ Speech engine initialized (Windows SAPI)")
                return
            except ImportError:
                print("⚠️ Windows SAPI not available, trying pyttsx3...")
            except Exception as e:
                print(f"⚠️ SAPI initialization failed: {e}, trying pyttsx3...")
        
        # Method 2: Try pyttsx3
        try:
            import pyttsx3
            # Create engine in worker thread to avoid conflicts
            self.use_pyttsx3 = True
            print("✅ Speech engine initialized (pyttsx3)")
            return
        except Exception as e:
            print(f"❌ pyttsx3 initialization failed: {e}")
        
        print("❌ No speech engine available")
    
    def speak(self, text: str, interrupt: bool = False):
        """
        Add text to speech queue with smart queue management
        
        Args:
            text: Text to speak
            interrupt: If True, clear queue and speak immediately
        """
        if not text or not text.strip():
            return
            
        if interrupt:
            self.clear_queue()
        else:
            # Smart queue management - keep only latest descriptions
            self._manage_queue_size()
            
        speech_item = {
            'text': text.strip(),
            'timestamp': time.time()
        }
        
        self.speech_queue.put(speech_item)
        print(f"🔊 Queued: {text[:50]}... (Queue size: {self.speech_queue.qsize()})")
    
    def _manage_queue_size(self):
        """Keep queue size manageable - remove old items if queue is full"""
        if self.speech_queue.qsize() >= self.max_queue_size:
            # Remove oldest items, keep only the most recent
            items_to_keep = []
            while not self.speech_queue.empty():
                try:
                    item = self.speech_queue.get_nowait()
                    items_to_keep.append(item)
                except queue.Empty:
                    break
            
            # Keep only the most recent items
            recent_items = items_to_keep[-1:] if items_to_keep else []
            
            # Put back the recent items
            for item in recent_items:
                self.speech_queue.put(item)
                
            if len(items_to_keep) > len(recent_items):
                print(f"🔇 Removed {len(items_to_keep) - len(recent_items)} old descriptions from queue")
    
    def speak_immediate(self, text: str):
        """Speak text immediately, bypassing queue"""
        if not text or not text.strip():
            return
            
        print(f"🔊 Speaking immediately: {text}")
        
        try:
            text = self._clean_text(text.strip())
            
            # Method 1: Windows SAPI (most reliable)
            if self.use_sapi:
                self.sapi.Speak(text)
                return
            
            # Method 2: pyttsx3
            if self.use_pyttsx3:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', config.SPEECH_RATE)
                engine.setProperty('volume', config.SPEECH_VOLUME)
                engine.say(text)
                engine.runAndWait()
                del engine
                return
            
            print("❌ No speech engine available")
                
        except Exception as e:
            print(f"❌ Immediate speech error: {e}")
    
    def _speech_worker(self):
        """Worker thread that processes speech queue"""
        while self.running:
            try:
                # Get next speech item
                speech_item = self.speech_queue.get(timeout=1.0)
                
                if speech_item:
                    self.is_speaking = True
                    text = speech_item['text']
                    
                    # Clean text for better speech
                    text = self._clean_text(text)
                    
                    print(f"🔊 Speaking: {text}")
                    
                    try:
                        # Method 1: Windows SAPI
                        if self.use_sapi:
                            self.sapi.Speak(text)
                        
                        # Method 2: pyttsx3
                        elif self.use_pyttsx3:
                            import pyttsx3
                            engine = pyttsx3.init()
                            engine.setProperty('rate', config.SPEECH_RATE)
                            engine.setProperty('volume', config.SPEECH_VOLUME)
                            engine.say(text)
                            engine.runAndWait()
                            del engine
                        
                        else:
                            print("❌ No speech engine available")
                            
                    except Exception as e:
                        print(f"❌ Speech error: {e}")
                    
                    self.is_speaking = False
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Speech worker error: {e}")
                self.is_speaking = False
    
    def _clean_text(self, text: str) -> str:
        """Clean text for better speech synthesis"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Replace common symbols
        replacements = {
            '&': 'and',
            '@': 'at',
            '%': 'percent',
            '#': 'number',
            'w/': 'with',
            'vs': 'versus'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def clear_queue(self):
        """Clear all pending speech"""
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break
        print("🔇 Speech queue cleared")
    
    def stop_current(self):
        """Stop current speech"""
        try:
            if self.use_sapi:
                self.sapi.Speak("", 1)  # Interrupt current speech
        except Exception as e:
            print(f"❌ Error stopping speech: {e}")
    
    def is_busy(self) -> bool:
        """Check if currently speaking or has items in queue"""
        return self.is_speaking or not self.speech_queue.empty()
    
    def wait_until_done(self, timeout: float = 30.0):
        """Wait until all speech is complete"""
        start_time = time.time()
        while self.is_busy() and (time.time() - start_time) < timeout:
            time.sleep(0.1)
    
    def shutdown(self):
        """Shutdown speech engine"""
        print("🔇 Shutting down speech engine...")
        self.running = False
        self.clear_queue()
        self.stop_current()
        
        if hasattr(self, 'speech_thread'):
            self.speech_thread.join(timeout=2.0)
            
        # Clean up resources
        try:
            if self.use_sapi and hasattr(self, 'sapi'):
                del self.sapi
        except:
            pass
                
        print("✅ Speech engine shutdown complete")