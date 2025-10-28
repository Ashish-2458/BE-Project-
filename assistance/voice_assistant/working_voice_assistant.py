"""
Working Voice Assistant - Pure voice interaction
Optimized for Windows with better microphone handling
"""
import sys
import os
import time
import speech_recognition as sr
import requests
import threading

# Add paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from OneVision.modules.speech import TextToSpeech
import config

class WorkingVoiceAssistant:
    """Voice assistant optimized for Windows"""
    
    def __init__(self):
        print("🤖 Initializing Voice Assistant...")
        
        # Initialize TTS
        self.tts = TextToSpeech()
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Use the Realtek microphone (index 1 from our check)
        try:
            self.microphone = sr.Microphone(device_index=1)  # Realtek microphone
            print("🎤 Using Realtek microphone")
        except:
            self.microphone = sr.Microphone()  # Fallback to default
            print("🎤 Using default microphone")
        
        # Optimize recognizer settings
        self.recognizer.energy_threshold = 4000  # Higher threshold for noisy environments
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.0  # 1 second of silence ends phrase
        self.recognizer.phrase_threshold = 0.3
        
        print("✅ Voice Assistant ready!")
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        print("🔧 Calibrating microphone...")
        self.tts.speak_immediate("Calibrating microphone. Please be quiet for a moment.")
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("✅ Microphone calibrated")
            return True
        except Exception as e:
            print(f"❌ Calibration failed: {e}")
            return False
    
    def listen_for_speech(self):
        """Listen for user speech"""
        print("\n" + "="*50)
        print("🎤 READY TO LISTEN - Speak your question now!")
        print("="*50)
        
        try:
            with self.microphone as source:
                # Listen with reasonable timeouts
                audio = self.recognizer.listen(
                    source,
                    timeout=10,  # Wait 10 seconds for speech to start
                    phrase_time_limit=15  # Allow 15 seconds of speech
                )
            
            print("🧠 Converting speech to text...")
            
            # Try Google Speech Recognition
            try:
                text = self.recognizer.recognize_google(audio, language='en-US')
                print(f"👤 You said: '{text}'")
                return text.strip()
                
            except sr.UnknownValueError:
                print("❌ Could not understand speech")
                return "UNCLEAR"
                
            except sr.RequestError as e:
                print(f"❌ Speech service error: {e}")
                return "ERROR"
        
        except sr.WaitTimeoutError:
            print("⏰ No speech detected")
            return "TIMEOUT"
            
        except Exception as e:
            print(f"❌ Listening error: {e}")
            return "ERROR"
    
    def get_ai_response(self, question):
        """Get AI response from Gemini"""
        print("🧠 Getting AI response...")
        
        prompt = f"""You are a helpful AI voice assistant.

User said: "{question}"

Provide a clear, helpful response in 1-2 sentences. Be conversational and friendly.

Response:"""
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'X-goog-api-key': config.GEMINI_API_KEY
            }
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 80
                }
            }
            
            response = requests.post(
                config.GEMINI_API_URL,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['candidates'][0]['content']['parts'][0]['text']
                return ai_response.strip()
            else:
                return "Sorry, I'm having trouble thinking right now."
                
        except Exception as e:
            print(f"❌ AI error: {e}")
            return "Sorry, I encountered an error."
    
    def speak_response(self, response):
        """Speak the response and wait for completion"""
        print(f"🤖 Assistant: {response}")
        self.tts.speak_immediate(response)
        
        # Calculate proper wait time for speech to complete
        words = len(response.split())
        # More generous timing: 0.8 seconds per word + 2 second buffer
        wait_time = max(4, words * 0.8 + 2)
        
        print(f"🔊 Speaking... (waiting {wait_time:.1f} seconds)")
        time.sleep(wait_time)
        print("✅ Speech completed")
    
    def start(self):
        """Start the voice assistant"""
        print("🚀 Starting Voice Assistant")
        print("=" * 40)
        
        # Calibrate microphone
        if not self.calibrate_microphone():
            print("❌ Cannot start without microphone")
            return
        
        time.sleep(2)
        
        # Welcome message
        welcome = "Hello! I'm your voice assistant. Speak to me and I'll respond. Say goodbye to stop."
        print(f"🤖 {welcome}")
        self.speak_response(welcome)
        
        print("🎤 Voice assistant is now ready for your questions!")
        
        # Main loop
        try:
            while True:
                # Listen for user
                user_speech = self.listen_for_speech()
                
                if user_speech == "TIMEOUT":
                    self.speak_response("I'm still here. Please speak if you have a question.")
                    continue
                elif user_speech == "UNCLEAR":
                    self.speak_response("I didn't understand. Please speak clearly.")
                    continue
                elif user_speech == "ERROR":
                    self.speak_response("There was an error. Please try again.")
                    continue
                elif not user_speech:
                    continue
                
                # Check for exit
                if any(word in user_speech.lower() for word in ['goodbye', 'exit', 'quit', 'stop', 'bye']):
                    self.speak_response("Goodbye! Have a great day!")
                    break
                
                # Get and speak AI response
                ai_response = self.get_ai_response(user_speech)
                self.speak_response(ai_response)
                
                # Extra pause to ensure speech is completely finished
                print("⏳ Ready for next question...")
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")
            self.speak_response("Goodbye!")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            time.sleep(2)
            self.tts.shutdown()
            print("✅ Voice assistant stopped")

def main():
    """Main function"""
    print("🎤 Pure Voice Assistant")
    print("Speak to AI, AI speaks back!")
    print("Make sure your microphone is unmuted.\n")
    
    assistant = WorkingVoiceAssistant()
    assistant.start()

if __name__ == "__main__":
    main()