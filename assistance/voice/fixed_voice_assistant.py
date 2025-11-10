"""
Fixed Voice Assistant with Working Audio
Uses the same TTS system from OneVision that was working
"""
import speech_recognition as sr
import requests
import json
import time
import sys
import os

# Add path to use OneVision TTS module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from OneVision.modules.speech import TextToSpeech

# Configuration
GEMINI_API_KEY = "AIzaSyBBcYQyL8YJpzE1PkrJbTEcephbly1-BoU"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

class FixedVoiceAssistant:
    def __init__(self):
        """Initialize voice assistant with working audio"""
        print("🤖 Starting Voice Assistant with Fixed Audio...")
        
        # Setup speech recognition
        self.recognizer = sr.Recognizer()
        self.setup_microphone()
        
        # Use OneVision TTS (this was working!)
        print("🔊 Initializing audio system...")
        self.tts = TextToSpeech(rate=150, volume=0.9)
        
        print("✅ Voice Assistant ready with working audio!")
    
    def setup_microphone(self):
        """Setup microphone"""
        print("🎤 Setting up microphone...")
        
        # Find Realtek microphone
        mic_list = sr.Microphone.list_microphone_names()
        for i, name in enumerate(mic_list):
            if 'realtek' in name.lower() or 'microphone array' in name.lower():
                try:
                    self.microphone = sr.Microphone(device_index=i)
                    print(f"✅ Using: {name}")
                    break
                except:
                    continue
        else:
            self.microphone = sr.Microphone()
            print("✅ Using default microphone")
        
        # Settings
        self.recognizer.energy_threshold = 4000
        self.recognizer.pause_threshold = 1.0
        
        # Calibrate
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ Microphone calibrated")
        except Exception as e:
            print(f"⚠️ Calibration warning: {e}")
    
    def test_audio(self):
        """Test audio output"""
        print("🧪 Testing audio output...")
        test_message = "Audio test - can you hear this loud and clear?"
        print(f"🔊 Testing: {test_message}")
        self.tts.speak_immediate(test_message)
        time.sleep(4)
        print("✅ Audio test completed")
    
    def listen(self):
        """Listen for user speech"""
        print("\n" + "="*60)
        print("🎤 READY TO LISTEN - Speak your question now!")
        print("="*60)
        
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source, 
                    timeout=15,  # Wait 15 seconds
                    phrase_time_limit=20  # Allow 20 seconds of speech
                )
            
            print("🧠 Converting speech to text...")
            
            text = self.recognizer.recognize_google(audio, language='en-US')
            print(f"👤 You said: '{text}'")
            return text.strip()
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected")
            return "TIMEOUT"
        except sr.UnknownValueError:
            print("❌ Could not understand speech")
            return "UNCLEAR"
        except Exception as e:
            print(f"❌ Error: {e}")
            return "ERROR"
    
    def get_ai_response(self, user_text):
        """Get AI response"""
        print("🧠 Getting AI response...")
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': GEMINI_API_KEY
        }
        
        prompt = f"""You are a helpful voice assistant.

User said: "{user_text}"

Respond in a friendly, conversational way. Keep it short - 1 to 2 sentences maximum.

Response:"""
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 60
            }
        }
        
        try:
            response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result['candidates'][0]['content']['parts'][0]['text']
                return ai_text.strip()
            else:
                return "Sorry, I'm having trouble right now."
                
        except Exception as e:
            print(f"❌ AI error: {e}")
            return "Sorry, I had an error."
    
    def speak(self, text):
        """Speak text using working TTS"""
        print(f"🤖 Assistant: {text}")
        print("🔊 Speaking response...")
        
        # Use the working TTS system
        self.tts.speak_immediate(text)
        
        # Wait for speech to complete
        words = len(text.split())
        wait_time = max(3, words * 0.6)  # 0.6 seconds per word, minimum 3 seconds
        time.sleep(wait_time)
        
        print("✅ Speech completed")
    
    def run(self):
        """Main conversation loop"""
        print("🚀 Starting Voice Assistant")
        print("=" * 60)
        
        # Test audio first
        self.test_audio()
        
        # Welcome message
        welcome = "Hello! I'm your voice assistant. Ask me anything. Say goodbye to exit."
        self.speak(welcome)
        
        # Main conversation loop
        conversation_count = 0
        
        while True:
            try:
                conversation_count += 1
                print(f"\n--- Conversation {conversation_count} ---")
                
                # Listen for user
                user_input = self.listen()
                
                # Handle responses
                if user_input == "TIMEOUT":
                    self.speak("I'm still listening. Please speak your question.")
                    continue
                elif user_input == "UNCLEAR":
                    self.speak("I didn't understand. Please speak clearly.")
                    continue
                elif user_input == "ERROR":
                    self.speak("There was an error. Please try again.")
                    continue
                
                # Check for exit
                if any(word in user_input.lower() for word in ['goodbye', 'bye', 'exit', 'quit', 'stop']):
                    self.speak("Goodbye! Have a great day!")
                    break
                
                # Get and speak AI response
                ai_response = self.get_ai_response(user_input)
                self.speak(ai_response)
                
                print("🎯 Ready for next question...")
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n🛑 Interrupted")
                self.speak("Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Cleanup
        self.tts.shutdown()
        print("✅ Voice Assistant stopped")

def main():
    """Main function"""
    print("🎤 Fixed Voice Assistant")
    print("Using the same audio system that was working in OneVision")
    print("Make sure your speakers/headphones are on and volume is up!\n")
    
    try:
        assistant = FixedVoiceAssistant()
        assistant.run()
    except Exception as e:
        print(f"❌ Failed to start: {e}")

if __name__ == "__main__":
    main()