"""
Simple Voice Assistant - Optimized for Windows
Clean implementation with better microphone handling
"""
import speech_recognition as sr
import pyttsx3
import requests
import json
import time

# Configuration
GEMINI_API_KEY = "AIzaSyBBcYQyL8YJpzE1PkrJbTEcephbly1-BoU"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

class SimpleVoiceAssistant:
    def __init__(self):
        """Initialize voice assistant"""
        print("🤖 Starting Simple Voice Assistant...")
        
        # Setup speech recognition
        self.recognizer = sr.Recognizer()
        
        # Find best microphone
        self.setup_microphone()
        
        # Setup text-to-speech
        self.setup_tts()
        
        print("✅ Voice Assistant initialized!")
    
    def setup_microphone(self):
        """Setup microphone with optimal settings"""
        print("🎤 Setting up microphone...")
        
        # Try different microphones
        mic_list = sr.Microphone.list_microphone_names()
        print(f"Found {len(mic_list)} microphones")
        
        # Try Realtek first (usually works best on Windows)
        for i, name in enumerate(mic_list):
            if 'realtek' in name.lower() or 'microphone array' in name.lower():
                try:
                    self.microphone = sr.Microphone(device_index=i)
                    print(f"✅ Using: {name}")
                    break
                except:
                    continue
        else:
            # Fallback to default
            self.microphone = sr.Microphone()
            print("✅ Using default microphone")
        
        # Optimize recognizer settings
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 1.2  # Longer pause before ending
        self.recognizer.phrase_threshold = 0.3
        
        # Calibrate
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ Microphone calibrated")
        except Exception as e:
            print(f"⚠️ Calibration warning: {e}")
    
    def setup_tts(self):
        """Setup text-to-speech"""
        print("🔊 Setting up text-to-speech...")
        
        try:
            self.tts = pyttsx3.init()
            
            # Set properties
            self.tts.setProperty('rate', 160)  # Slightly faster
            self.tts.setProperty('volume', 0.95)  # Louder
            
            # Try to use a better voice if available
            voices = self.tts.getProperty('voices')
            if voices:
                # Prefer female voice if available
                for voice in voices:
                    if 'zira' in voice.name.lower() or 'female' in voice.name.lower():
                        self.tts.setProperty('voice', voice.id)
                        break
            
            print("✅ Text-to-speech ready")
            
        except Exception as e:
            print(f"❌ TTS setup failed: {e}")
    
    def listen(self):
        """Listen for user speech"""
        print("\n" + "="*50)
        print("🎤 LISTENING - Speak your question now!")
        print("="*50)
        
        try:
            with self.microphone as source:
                # Listen with generous timeouts
                audio = self.recognizer.listen(
                    source, 
                    timeout=12,  # Wait 12 seconds for speech
                    phrase_time_limit=20  # Allow 20 seconds of speech
                )
            
            print("🧠 Processing your speech...")
            
            # Convert to text
            text = self.recognizer.recognize_google(audio, language='en-US')
            print(f"👤 You said: '{text}'")
            return text.strip()
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected - try again")
            return "TIMEOUT"
        except sr.UnknownValueError:
            print("❌ Could not understand - please speak clearly")
            return "UNCLEAR"
        except Exception as e:
            print(f"❌ Listening error: {e}")
            return "ERROR"
    
    def get_ai_response(self, user_text):
        """Get response from Gemini AI"""
        print("🧠 Thinking...")
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': GEMINI_API_KEY
        }
        
        prompt = f"""You are a helpful voice assistant. 

User said: "{user_text}"

Respond in a conversational, friendly way. Keep it to 1-2 sentences. Be helpful and natural.

Response:"""
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 80
            }
        }
        
        try:
            response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                ai_text = result['candidates'][0]['content']['parts'][0]['text']
                return ai_text.strip()
            else:
                return "Sorry, I'm having trouble connecting to my brain right now."
                
        except Exception as e:
            print(f"❌ AI error: {e}")
            return "Sorry, I encountered an error while thinking."
    
    def speak(self, text):
        """Speak text aloud"""
        print(f"🤖 Assistant: {text}")
        
        try:
            self.tts.say(text)
            self.tts.runAndWait()
            
            # Calculate wait time based on text length
            words = len(text.split())
            wait_time = max(2, words * 0.4)  # 0.4 seconds per word, minimum 2 seconds
            
            print(f"🔊 Speaking complete (waited {wait_time:.1f}s)")
            time.sleep(wait_time)  # Extra buffer
            
        except Exception as e:
            print(f"❌ Speech error: {e}")
    
    def run(self):
        """Main conversation loop"""
        print("🚀 Simple Voice Assistant Started")
        print("=" * 50)
        
        # Welcome
        welcome = "Hello! I'm your voice assistant. Ask me anything or say goodbye to exit."
        self.speak(welcome)
        
        # Main loop
        conversation_count = 0
        
        while True:
            try:
                conversation_count += 1
                print(f"\n--- Conversation {conversation_count} ---")
                
                # Listen for user
                user_input = self.listen()
                
                # Handle special cases
                if user_input == "TIMEOUT":
                    self.speak("I'm still here. Please speak if you have a question.")
                    continue
                elif user_input == "UNCLEAR":
                    self.speak("I didn't catch that. Please speak more clearly.")
                    continue
                elif user_input == "ERROR":
                    self.speak("There was an error. Let's try again.")
                    continue
                
                # Check for exit
                if any(word in user_input.lower() for word in ['goodbye', 'bye', 'exit', 'quit', 'stop']):
                    self.speak("Goodbye! Have a wonderful day!")
                    break
                
                # Get AI response
                ai_response = self.get_ai_response(user_input)
                
                # Speak response
                self.speak(ai_response)
                
                # Ready for next question
                print("✅ Ready for next question...")
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n🛑 Interrupted")
                self.speak("Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                self.speak("Something went wrong. Let's try again.")
        
        print("✅ Voice Assistant stopped")

def main():
    """Main function"""
    print("🎤 Simple Voice Assistant")
    print("Pure voice interaction - speak and listen!")
    print("Make sure your microphone is unmuted.\n")
    
    try:
        assistant = SimpleVoiceAssistant()
        assistant.run()
    except Exception as e:
        print(f"❌ Failed to start: {e}")

if __name__ == "__main__":
    main()