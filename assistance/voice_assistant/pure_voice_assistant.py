"""
Pure Voice Assistant - Speak to AI, AI speaks back
No typing, pure voice interaction
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

class PureVoiceAssistant:
    """Pure voice interaction - speak and listen only"""
    
    def __init__(self):
        print("🤖 Initializing Pure Voice Assistant...")
        
        # Initialize components
        self.tts = TextToSpeech()
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        # Find working microphone
        self.setup_microphone()
        
        print("✅ Pure Voice Assistant ready!")
    
    def setup_microphone(self):
        """Setup microphone with better settings"""
        print("🎤 Setting up microphone...")
        
        # List available microphones
        mic_list = sr.Microphone.list_microphone_names()
        print(f"Found {len(mic_list)} microphones:")
        for i, name in enumerate(mic_list[:5]):  # Show first 5
            print(f"  {i}: {name}")
        
        # Try default microphone first
        try:
            self.microphone = sr.Microphone()
            
            # Adjust recognizer settings for better performance
            self.recognizer.energy_threshold = 300  # Minimum audio energy
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8  # Seconds of silence to end phrase
            self.recognizer.phrase_threshold = 0.3  # Minimum seconds of speaking
            
            # Calibrate for ambient noise
            print("🔧 Calibrating microphone... (please be quiet for 2 seconds)")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            
            print("✅ Microphone setup complete!")
            
        except Exception as e:
            print(f"❌ Microphone setup failed: {e}")
            print("💡 Try checking Windows microphone permissions")
    
    def listen_for_speech(self):
        """Listen for user speech with better error handling"""
        print("\n🎤 Listening... Speak now!")
        
        try:
            with self.microphone as source:
                # Listen with longer timeouts
                audio = self.recognizer.listen(
                    source,
                    timeout=15,  # Wait up to 15 seconds for speech to start
                    phrase_time_limit=20  # Allow up to 20 seconds of continuous speech
                )
            
            print("🧠 Processing your speech...")
            
            # Convert to text
            try:
                text = self.recognizer.recognize_google(audio, language='en-US')
                print(f"👤 You said: '{text}'")
                return text
                
            except sr.UnknownValueError:
                print("❌ Could not understand speech")
                self.tts.speak_immediate("Sorry, I couldn't understand what you said. Please speak clearly and try again.")
                return None
                
            except sr.RequestError as e:
                print(f"❌ Speech recognition error: {e}")
                self.tts.speak_immediate("Sorry, there's an issue with speech recognition. Please try again.")
                return None
        
        except sr.WaitTimeoutError:
            print("⏰ No speech detected")
            self.tts.speak_immediate("I didn't hear anything. Please try speaking again.")
            return None
            
        except Exception as e:
            print(f"❌ Listening error: {e}")
            self.tts.speak_immediate("There was an error listening. Please try again.")
            return None
    
    def get_ai_response(self, question):
        """Get AI response"""
        print("🧠 Getting AI response...")
        
        prompt = f"""You are a helpful AI voice assistant for visually impaired users.

User question: "{question}"

Provide a clear, conversational response in 2-3 sentences. Be helpful and supportive.
Avoid visual references unless specifically asked about them.

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
                    "maxOutputTokens": 120,
                    "topP": 0.8
                }
            }
            
            response = requests.post(
                config.GEMINI_API_URL,
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['candidates'][0]['content']['parts'][0]['text']
                return ai_response.strip()
            else:
                return "Sorry, I'm having trouble thinking right now. Please try again."
                
        except Exception as e:
            print(f"❌ AI error: {e}")
            return "Sorry, I encountered an error. Please try your question again."
    
    def speak_response(self, response):
        """Speak AI response"""
        print(f"🤖 Assistant: {response}")
        self.tts.speak_immediate(response)
        
        # Wait for speech to complete
        words = len(response.split())
        wait_time = max(3, words * 0.5)  # At least 3 seconds
        time.sleep(wait_time)
    
    def test_microphone(self):
        """Test microphone before starting"""
        print("🧪 Testing microphone...")
        self.tts.speak_immediate("Testing microphone. Please say hello when you hear this.")
        
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
            
            text = self.recognizer.recognize_google(audio)
            print(f"✅ Microphone test successful! Heard: {text}")
            self.tts.speak_immediate("Great! Microphone is working perfectly.")
            return True
            
        except Exception as e:
            print(f"❌ Microphone test failed: {e}")
            self.tts.speak_immediate("Microphone test failed. Please check your microphone settings.")
            return False
    
    def start(self):
        """Start the pure voice assistant"""
        print("🚀 Starting Pure Voice Assistant")
        print("=" * 50)
        
        # Test microphone first
        if not self.test_microphone():
            print("❌ Cannot start without working microphone")
            return
        
        time.sleep(2)
        
        # Welcome
        welcome = "Hello! I'm your voice assistant. Just speak to me and I'll respond. Say goodbye to stop."
        print(f"🤖 {welcome}")
        self.tts.speak_immediate(welcome)
        
        time.sleep(3)
        
        # Main conversation loop
        try:
            conversation_count = 0
            
            while True:
                conversation_count += 1
                print(f"\n--- Conversation {conversation_count} ---")
                
                # Listen for user input
                user_speech = self.listen_for_speech()
                
                if user_speech:
                    # Check for exit commands
                    if any(word in user_speech.lower() for word in ['goodbye', 'exit', 'quit', 'stop', 'bye']):
                        goodbye = "Goodbye! It was nice talking with you. Have a great day!"
                        self.speak_response(goodbye)
                        break
                    
                    # Get AI response
                    ai_response = self.get_ai_response(user_speech)
                    
                    # Speak response
                    self.speak_response(ai_response)
                
                # Small pause between conversations
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")
            self.tts.speak_immediate("Goodbye!")
        except Exception as e:
            print(f"❌ Error: {e}")
            self.tts.speak_immediate("Sorry, something went wrong. Goodbye!")
        finally:
            time.sleep(2)
            self.tts.shutdown()
            print("✅ Voice assistant stopped")

def main():
    """Main function"""
    print("🎤 Pure Voice Assistant")
    print("Speak to AI, AI speaks back - no typing needed!")
    print("Make sure your microphone is connected and working.\n")
    
    assistant = PureVoiceAssistant()
    assistant.start()

if __name__ == "__main__":
    main()