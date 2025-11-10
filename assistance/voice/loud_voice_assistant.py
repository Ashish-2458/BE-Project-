"""
LOUD Voice Assistant - Maximum volume for better hearing
"""
import speech_recognition as sr
import requests
import time
import sys
import os

# Add path to OneVision
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Configuration
GEMINI_API_KEY = "AIzaSyBBcYQyL8YJpzE1PkrJbTEcephbly1-BoU"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

class LoudVoiceAssistant:
    def __init__(self):
        """Initialize with LOUD audio"""
        print("🤖 Starting LOUD Voice Assistant...")
        
        # Setup microphone
        self.setup_microphone()
        
        # Setup LOUD audio using Windows SAPI (most reliable)
        self.setup_loud_audio()
        
        print("✅ LOUD Voice Assistant ready!")
    
    def setup_microphone(self):
        """Setup microphone"""
        print("🎤 Setting up microphone...")
        
        self.recognizer = sr.Recognizer()
        
        # Find best microphone
        mic_list = sr.Microphone.list_microphone_names()
        for i, name in enumerate(mic_list):
            if 'realtek' in name.lower():
                self.microphone = sr.Microphone(device_index=i)
                print(f"✅ Using: {name}")
                break
        else:
            self.microphone = sr.Microphone()
            print("✅ Using default microphone")
        
        # Settings
        self.recognizer.energy_threshold = 4000
        self.recognizer.pause_threshold = 1.0
        
        # Calibrate
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Microphone ready")
    
    def setup_loud_audio(self):
        """Setup LOUD audio using Windows SAPI"""
        print("🔊 Setting up LOUD audio...")
        
        try:
            import win32com.client
            self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
            self.speaker.Volume = 100  # MAXIMUM VOLUME
            self.speaker.Rate = 2  # FASTER SPEECH for quicker responses
            
            print("✅ Windows SAPI audio ready at MAXIMUM VOLUME")
            self.audio_method = "SAPI"
            
        except Exception as e:
            print(f"⚠️ SAPI failed: {e}")
            print("🔊 Falling back to pyttsx3...")
            
            try:
                import pyttsx3
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 200)  # FASTER SPEECH
                self.tts_engine.setProperty('volume', 1.0)  # Maximum volume
                
                print("✅ pyttsx3 audio ready at maximum volume")
                self.audio_method = "pyttsx3"
                
            except Exception as e2:
                print(f"❌ All audio methods failed: {e2}")
                self.audio_method = None
    
    def speak_loud(self, text):
        """Speak text LOUDLY and FAST"""
        print(f"🤖 Assistant: {text}")
        print("🔊 SPEAKING FAST...")
        
        try:
            if self.audio_method == "SAPI":
                self.speaker.Speak(text)
            elif self.audio_method == "pyttsx3":
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            else:
                print("❌ No audio method available")
                return
            
            # Shorter wait time for faster response
            words = len(text.split())
            wait_time = max(1, words * 0.3)  # Much faster: 0.3 seconds per word, minimum 1 second
            time.sleep(wait_time)
            
            print("✅ Speech completed - Ready immediately!")
            
        except Exception as e:
            print(f"❌ Speech error: {e}")
    
    def listen(self):
        """Listen for speech"""
        print("\n" + "🎤" * 30)
        print("🎤 LISTENING NOW - SPEAK YOUR QUESTION!")
        print("🎤" * 30)
        
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=15, phrase_time_limit=20)
            
            print("🧠 Processing speech...")
            text = self.recognizer.recognize_google(audio)
            print(f"👤 You said: '{text}'")
            return text.strip()
            
        except sr.WaitTimeoutError:
            return "TIMEOUT"
        except sr.UnknownValueError:
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
        
        data = {
            "contents": [{"parts": [{"text": f"User said: '{user_text}'. Respond in 1-2 sentences, be helpful and friendly."}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 50}
        }
        
        try:
            response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text'].strip()
            else:
                return "Sorry, I'm having trouble right now."
        except:
            return "Sorry, I had an error."
    
    def run(self):
        """Main loop"""
        print("🚀 LOUD Voice Assistant Started")
        print("=" * 60)
        
        # LOUD welcome
        welcome = "HELLO! I AM YOUR LOUD VOICE ASSISTANT! ASK ME ANYTHING!"
        self.speak_loud(welcome)
        
        conversation_count = 0
        
        while True:
            try:
                conversation_count += 1
                print(f"\n--- CONVERSATION {conversation_count} ---")
                
                # Listen
                user_input = self.listen()
                
                if user_input == "TIMEOUT":
                    self.speak_loud("I AM STILL HERE! PLEASE SPEAK YOUR QUESTION!")
                    continue
                elif user_input == "UNCLEAR":
                    self.speak_loud("I DID NOT UNDERSTAND! PLEASE SPEAK CLEARLY!")
                    continue
                elif user_input == "ERROR":
                    self.speak_loud("THERE WAS AN ERROR! PLEASE TRY AGAIN!")
                    continue
                
                # Check exit
                if any(word in user_input.lower() for word in ['goodbye', 'bye', 'exit', 'quit', 'stop']):
                    self.speak_loud("GOODBYE! HAVE A GREAT DAY!")
                    break
                
                # Get and speak response
                ai_response = self.get_ai_response(user_input)
                self.speak_loud(ai_response.upper())  # Make response LOUD
                
                # NO DELAY - immediately ready for next question
                print("🎯 IMMEDIATELY READY FOR NEXT QUESTION!")
                
            except KeyboardInterrupt:
                print("\n🛑 Interrupted")
                self.speak_loud("GOODBYE!")
                break
        
        print("✅ LOUD Voice Assistant stopped")

def main():
    """Main function"""
    print("🔊 LOUD VOICE ASSISTANT")
    print("MAXIMUM VOLUME FOR BETTER HEARING!")
    print("Make sure your speakers are ON and volume is UP!\n")
    
    # Check Windows volume
    print("💡 AUDIO CHECKLIST:")
    print("1. Turn up your speaker/headphone volume")
    print("2. Check Windows volume (should be 70%+)")
    print("3. Make sure speakers are powered on")
    print("4. Check if headphones are plugged in correctly\n")
    
    try:
        assistant = LoudVoiceAssistant()
        assistant.run()
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    main()