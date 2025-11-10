import pyttsx3
import threading
import queue
import time
import sys
from typing import Optional

class TextToSpeech:
    """Text-to-speech engine with queue management for smooth audio feedback"""
    
    def __init__(self, rate: int = 150, volume: float = 0.9):
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.running = True
        self.rate = rate
        self.volume = volume
        
        # Use Windows SAPI directly for better reliability
        self.use_sapi = sys.platform == 'win32'
        
        if self.use_sapi:
            try:
                import win32com.client
                self.sapi_available = True
            except ImportError:
                self.sapi_available = False
                self.use_sapi = False
        
        # Start speech processing thread
        self.speech_thread = threading.Thread(target=self._speech_worker)
        self.speech_thread.daemon = True
        self.speech_thread.start()
        
        print("Text-to-speech initialized")
    
    def speak(self, text: str, priority: bool = False, interrupt: bool = False):
        """
        Add text to speech queue with smart queue management
        
        Args:
            text: Text to speak
            priority: If True, add to front of queue
            interrupt: If True, stop current speech and speak immediately
        """
        if not text or not text.strip():
            return
        
        current_time = time.time()
        
        if interrupt:
            self.stop_current_speech()
            # Clear entire queue for immediate response
            self._clear_queue_internal()
        
        # Smart queue management - keep only latest 3 items
        queue_size = self.speech_queue.qsize()
        if queue_size >= 3:
            # Remove oldest items, keep only the most recent 2
            all_items = []
            while not self.speech_queue.empty():
                try:
                    all_items.append(self.speech_queue.get_nowait())
                except queue.Empty:
                    break
            
            # Keep only the latest 2 items if queue is full
            if len(all_items) >= 3:
                items_to_keep = all_items[-2:]  # Keep the 2 most recent
                items_removed = len(all_items) - 2
                if items_removed > 0:
                    print(f"🗑️  Discarded {items_removed} old speech items")
            else:
                items_to_keep = all_items
            
            # Put back items to keep
            for item in items_to_keep:
                self.speech_queue.put(item)
        
        # Add new speech item
        speech_item = {
            'text': text.strip(),
            'timestamp': current_time,
            'priority': priority
        }
        
        if priority and not interrupt:
            # For priority items, add to front
            items = []
            while not self.speech_queue.empty():
                try:
                    items.append(self.speech_queue.get_nowait())
                except queue.Empty:
                    break
            
            # Put priority item first
            self.speech_queue.put(speech_item)
            # Put back other items (but limit to 1 more)
            for i, item in enumerate(items):
                if i < 1:  # Only keep 1 additional item
                    self.speech_queue.put(item)
        else:
            self.speech_queue.put(speech_item)
    
    def _speech_worker(self):
        """Worker thread that processes speech queue"""
        while self.running:
            try:
                # Get next speech item (blocking with timeout)
                speech_item = self.speech_queue.get(timeout=1.0)
                
                if speech_item:
                    self.is_speaking = True
                    text = speech_item['text']
                    
                    # Clean up text for better speech
                    text = self._clean_text_for_speech(text)
                    
                    print(f"🔊 Speaking: {text}")
                    
                    # Use Windows SAPI for better reliability
                    if self.use_sapi and self.sapi_available:
                        try:
                            import win32com.client
                            speaker = win32com.client.Dispatch("SAPI.SpVoice")
                            # Set speech rate (0-10, default is 0)
                            speaker.Rate = min(max(-2, (self.rate - 150) // 25), 2)
                            speaker.Volume = int(self.volume * 100)
                            speaker.Speak(text)
                        except Exception as e:
                            print(f"❌ SAPI speech error: {e}")
                    else:
                        # Fallback to pyttsx3
                        try:
                            engine = pyttsx3.init()
                            engine.setProperty('rate', self.rate)
                            engine.setProperty('volume', self.volume)
                            engine.say(text)
                            engine.runAndWait()
                            del engine
                        except Exception as e:
                            print(f"❌ pyttsx3 speech error: {e}")
                    
                    self.is_speaking = False
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Speech worker error: {e}")
                self.is_speaking = False
    
    def _clean_text_for_speech(self, text: str) -> str:
        """Clean and optimize text for speech synthesis"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Replace common abbreviations for better pronunciation
        replacements = {
            'w/': 'with',
            '&': 'and',
            '@': 'at',
            '%': 'percent',
            '#': 'number',
            'vs': 'versus',
            'etc': 'etcetera'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def stop_current_speech(self):
        """Stop current speech immediately"""
        try:
            self.engine.stop()
        except:
            pass
    
    def clear_queue(self):
        """Clear all pending speech"""
        self._clear_queue_internal()
    
    def _clear_queue_internal(self):
        """Internal method to clear queue"""
        cleared_count = 0
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
                cleared_count += 1
            except queue.Empty:
                break
        if cleared_count > 0:
            print(f"🗑️  Cleared {cleared_count} pending speech items")
    
    def is_busy(self) -> bool:
        """Check if currently speaking or has items in queue"""
        return self.is_speaking or not self.speech_queue.empty()
    
    def speak_immediate(self, text: str):
        """Speak text immediately, interrupting current speech"""
        print(f"🔊 Immediate speech: {text}")
        
        # Clear queue and stop current speech
        self.clear_queue()
        
        # Use Windows SAPI for immediate speech
        if self.use_sapi and self.sapi_available:
            try:
                import win32com.client
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Rate = 0  # Normal speed
                speaker.Volume = int(self.volume * 100)
                speaker.Speak(text)
                return
            except Exception as e:
                print(f"❌ SAPI immediate speech error: {e}")
        
        # Fallback: add to queue with high priority
        self.speak(text, priority=True, interrupt=True)
    
    def shutdown(self):
        """Shutdown speech engine"""
        self.running = False
        self.clear_queue()
        self.stop_current_speech()
        if hasattr(self, 'speech_thread'):
            self.speech_thread.join(timeout=2.0)
        print("Text-to-speech shutdown")