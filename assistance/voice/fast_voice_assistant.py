"""
FAST Voice Assistant - Immediate responses, no delays
"""
import speech_recognition as sr
import requests
import time
import sys
import os

# Configuration
GEMINI_API_KEY = "AIzaSyBBcYQyL8YJpzE1PkrJbTEcephbly1-BoU"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

class FastVoiceAssistant:
    def __init__(self):
        """Initialize FAST voice assistant"""
        print("🚀 Starting FAST Voice Assistant...")
        
        # Setup microphone
        self.setup_microphone()
        
        # Setup FAST audio
        self.setup_fast_audio()
        
        print("✅ FAST Voice Assistant ready!")
    
    def setup_microphone(self):
        """Quick microphone setup"""
        self.recognizer = sr.Recognizer()
        
        # Find Realtek microphone quickly
        mic_list = sr.Microphone.list_microphone_names()
        for i, name in enumerate(mic_list):
            if 'realtek' in name.lower():
                self.microphone = sr.Microphone(device_index=i)
                break
        else:
            self.microphone = sr.Microphone()
        
        # Fast settings
        self.recognizer.energy_threshold = 4000
        self.recognizer.pause_threshold = 0.8  # Shorter pause = faster response
        
        # Quick calibration
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Faster calibration
        
        print("✅ Microphone ready")
    
    def setup_fast_audio(self):
        """Setup FAST audio"""
        try:
            import win32com.client
            self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
            self.speaker.Volume = 100  # Maximum volume
            self.speaker.Rate = 3  # FASTEST SPEECH RATE
            self.audio_method = "SAPI"
            print("✅ FAST Windows SAPI audio ready")
        except:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 220)  # Very fast
            self.tts_engine.setProperty('volume', 1.0)
            self.audio_method = "pyttsx3"
            print("✅ FAST pyttsx3 audio ready")
    
    def speak_fast(self, text):
        """Speak FAST with NO waiting"""
        print(f"🤖 {text}")
        
        if self.audio_method == "SAPI":
            self.speaker.Speak(text)
        else:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        
        # NO WAITING - return immediately
        print("🔊 Speaking...")
    
    def listen_fast(self):
        """Fast listening"""
        print("\n🎤 LISTENING - SPEAK NOW!")
        
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
            
            text = self.recognizer.recognize_google(audio)
            print(f"👤 '{text}'")
            return text.strip()
            
        except sr.WaitTimeoutError:
            return "TIMEOUT"
        except sr.UnknownValueError:
            return "UNCLEAR"
        except:
            return "ERROR"
    
    def get_fast_ai_response(self, user_text):
        """Get AI response quickly"""
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': GEMINI_API_KEY
        }
        
        data = {
            "contents": [{"parts": [{"text": f"User: '{user_text}'. Respond in 1 short sentence."}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 30}  # Shorter responses
        }
        
        try:
            response = requests.post(GEMINI_API_URL, headers=headers, json=data, timeout=5)  # Faster timeout
            if response.status_code == 200:
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text'].strip()
            else:
                return "Sorry, error occurred."
        except:
            return "Sorry, I had an issue."
    
    def run(self):
        """FAST main loop with NO delays"""
        print("🚀 FAST Voice Assistant Started - NO DELAYS!")
        print("=" * 50)
        
        # Fast welcome
        self.speak_fast("HELLO! FAST VOICE ASSISTANT READY!")
        
        conversation_count = 0
        
        while True:
            try:
                conversation_count += 1
                print(f"\n--- CONVERSATION {conversation_count} ---")
                
                # Listen immediately
                user_input = self.listen_fast()
                
                if user_input == "TIMEOUT":
                    self.speak_fast("STILL LISTENING!")
                    continue
                elif user_input == "UNCLEAR":
                    self.speak_fast("SPEAK CLEARLY!")
                    continue
                elif user_input == "ERROR":
                    self.speak_fast("TRY AGAIN!")
                    continue
                
                # Check exit
                if any(word in user_input.lower() for word in ['goodbye', 'bye', 'exit', 'quit', 'stop']):
                    self.speak_fast("GOODBYE!")
                    break
                
                # Get AI response
                print("🧠 AI thinking...")
                ai_response = self.get_fast_ai_response(user_input)
                
                # Speak response
                self.speak_fast(ai_response.upper())
                
                # IMMEDIATELY continue to next conversation - NO DELAYS!
                print("⚡ READY IMMEDIATELY!")
                
            except KeyboardInterrupt:
                print("\n🛑 Stopped")
                self.speak_fast("BYE!")
                break
        
        print("✅ FAST Assistant stopped")

def main():
    """Main function"""
    print("⚡ FAST VOICE ASSISTANT")
    print("IMMEDIATE RESPONSES - NO WAITING!")
    print("Speak clearly and close to microphone\n")
    
    try:
        assistant = FastVoiceAssistant()
        assistant.run()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()