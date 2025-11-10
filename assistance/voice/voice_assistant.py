"""
Simple Voice Assistant
User speaks -> AI responds with voice
"""
import speech_recognition as sr
import pyttsx3
import requests
import json
import time

# Configuration
GEMINI_API_KEY = "AIzaSyBBcYQyL8YJpzE1PkrJbTEcephbly1-BoU"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

class VoiceAssistant:
    def __init__(self):
        """Initialize the voice assistant"""
        print("🤖 Initializing Voice Assistant...")
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Speed of speech
        self.tts_engine.setProperty('volume', 0.9)  # Volume level
        
        # Calibrate microphone
        self.calibrate_microphone()
        
        print("✅ Voice Assistant ready!")
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        print("🎤 Calibrating microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Microphone calibrated")
    
    def listen_for_speech(self):
        """Listen for user speech and convert to text"""
        print("\n🎤 Listening... Speak now!")
        
        try:
            # Listen for audio
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
            
            print("🧠 Converting speech to text...")
            
            # Convert speech to text
            text = self.recognizer.recognize_google(audio)
            print(f"👤 You said: '{text}'")
            return text
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand speech")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def get_ai_response(self, user_text):
        """Get AI response from Gemini"""
        print("🧠 Getting AI response...")
        
        # Prepare the request
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': GEMINI_API_KEY
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"You are a helpful voice assistant. User said: '{user_text}'. Respond in 1-2 sentences, be conversational and helpful."
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 100
            }
        }
        
        try:
            # Make API request
            response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"🤖 AI Response: {ai_text}")
                return ai_text.strip()
            else:
                print(f"❌ API Error: {response.status_code}")
                return "Sorry, I'm having trouble thinking right now."
                
        except Exception as e:
            print(f"❌ AI Error: {e}")
            return "Sorry, I encountered an error."
    
    def speak_text(self, text):
        """Convert text to speech"""
        print(f"🔊 Speaking: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
        print("✅ Speech completed")
    
    def run(self):
        """Main conversation loop"""
        print("🚀 Starting Voice Assistant")
        print("=" * 50)
        
        # Welcome message
        welcome_msg = "Hello! I'm your voice assistant. Ask me anything. Say goodbye to exit."
        self.speak_text(welcome_msg)
        
        # Main conversation loop
        while True:
            try:
                # Listen for user input
                user_speech = self.listen_for_speech()
                
                if user_speech is None:
                    continue
                
                # Check for exit commands
                if any(word in user_speech.lower() for word in ['goodbye', 'exit', 'quit', 'bye', 'stop']):
                    goodbye_msg = "Goodbye! Have a great day!"
                    self.speak_text(goodbye_msg)
                    break
                
                # Get AI response
                ai_response = self.get_ai_response(user_speech)
                
                # Speak AI response
                self.speak_text(ai_response)
                
                # Brief pause before next interaction
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n🛑 Interrupted by user")
                self.speak_text("Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                self.speak_text("Sorry, something went wrong.")
        
        print("✅ Voice Assistant stopped")

def main():
    """Main function"""
    print("🎤 Simple Voice Assistant")
    print("Speak to me and I'll respond!")
    print("Make sure your microphone is working.\n")
    
    try:
        assistant = VoiceAssistant()
        assistant.run()
    except Exception as e:
        print(f"❌ Failed to start assistant: {e}")

if __name__ == "__main__":
    main()