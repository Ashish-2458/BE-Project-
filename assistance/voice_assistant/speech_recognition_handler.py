"""
Speech recognition handler for voice input
"""
import speech_recognition as sr
import threading
import time
from typing import Optional, Callable
import config

class SpeechRecognitionHandler:
    """Handles voice input and wake word detection"""
    
    def __init__(self, on_speech_callback: Callable[[str], None]):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(device_index=config.MICROPHONE_DEVICE_INDEX)
        self.on_speech_callback = on_speech_callback
        self.is_listening = False
        self.listen_thread = None
        
        # Adjust for ambient noise
        print("🎤 Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        print("✅ Microphone calibrated")
    
    def start_listening(self):
        """Start continuous listening for wake words and commands"""
        if self.is_listening:
            return
        
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_continuously)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        print("🎤 Voice assistant listening...")
    
    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        if self.listen_thread:
            self.listen_thread.join(timeout=2)
        print("🔇 Voice assistant stopped listening")
    
    def _listen_continuously(self):
        """Continuous listening loop"""
        while self.is_listening:
            try:
                # Listen for audio
                with self.microphone as source:
                    print("🎤 Listening for voice...")
                    audio = self.recognizer.listen(
                        source, 
                        timeout=config.SPEECH_RECOGNITION_TIMEOUT,
                        phrase_time_limit=config.SPEECH_RECOGNITION_PHRASE_TIMEOUT
                    )
                
                # Recognize speech
                text = self._recognize_speech(audio)
                if text:
                    print(f"🗣️ Heard: {text}")
                    
                    # Check for wake words or process command
                    if self._contains_wake_word(text) or self._is_direct_command(text):
                        # Remove wake word from text
                        cleaned_text = self._clean_wake_words(text)
                        if cleaned_text.strip():
                            self.on_speech_callback(cleaned_text)
                        else:
                            # Just wake word, wait for command
                            self.on_speech_callback("Hello! How can I help you?")
                
            except sr.WaitTimeoutError:
                # Normal timeout, continue listening
                continue
            except sr.UnknownValueError:
                # Could not understand audio
                if config.DEBUG_MODE:
                    print("🤷 Could not understand audio")
                continue
            except sr.RequestError as e:
                print(f"❌ Speech recognition error: {e}")
                time.sleep(1)
            except Exception as e:
                print(f"❌ Listening error: {e}")
                time.sleep(1)
    
    def _recognize_speech(self, audio) -> Optional[str]:
        """Convert audio to text using speech recognition"""
        try:
            # Try Google Speech Recognition (free tier)
            text = self.recognizer.recognize_google(audio)
            return text.lower().strip()
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            # Fallback to offline recognition if available
            try:
                text = self.recognizer.recognize_sphinx(audio)
                return text.lower().strip()
            except:
                return None
    
    def _contains_wake_word(self, text: str) -> bool:
        """Check if text contains any wake words"""
        text_lower = text.lower()
        return any(wake_word.lower() in text_lower for wake_word in config.WAKE_WORDS)
    
    def _is_direct_command(self, text: str) -> bool:
        """Check if this seems like a direct command (no wake word needed)"""
        # If we're already in conversation mode, treat as direct command
        # For now, always require wake word for safety
        return False
    
    def _clean_wake_words(self, text: str) -> str:
        """Remove wake words from text to get the actual command"""
        text_lower = text.lower()
        
        for wake_word in config.WAKE_WORDS:
            wake_word_lower = wake_word.lower()
            if wake_word_lower in text_lower:
                # Remove wake word and clean up
                text = text_lower.replace(wake_word_lower, "").strip()
                # Remove common connecting words
                text = text.replace("please", "").replace("can you", "").strip()
                break
        
        return text
    
    def listen_once(self, timeout: int = 10) -> Optional[str]:
        """Listen for a single command with timeout"""
        try:
            print(f"🎤 Listening for {timeout} seconds...")
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            text = self._recognize_speech(audio)
            if text:
                print(f"🗣️ Heard: {text}")
                return text
            return None
            
        except sr.WaitTimeoutError:
            print("⏰ Listening timeout")
            return None
        except Exception as e:
            print(f"❌ Listen once error: {e}")
            return None
    
    def test_microphone(self) -> bool:
        """Test if microphone is working"""
        try:
            print("🎤 Testing microphone... Say something!")
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
            
            text = self._recognize_speech(audio)
            if text:
                print(f"✅ Microphone test successful! Heard: {text}")
                return True
            else:
                print("❌ Could not understand speech")
                return False
                
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            return False