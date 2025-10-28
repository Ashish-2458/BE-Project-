"""
Simple Voice Assistant - Just listen, ask AI, and speak back
"""
import sys
import os
import time
import speech_recognition as sr
import requests

# Add paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from OneVision.modules.speech import TextToSpeech
import config

class SimpleVoiceAssistant:
    """Simple voice assistant - listen, process, respond"""
    
    def __init__(self):
        print("🤖 Initializing Simple Voice Assistant...")
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech
        self.tts = TextToSpeech()
        
        # Adjust for ambient noise
        print("🎤 Calibrating microphone...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
        
        print("✅ Voice Assistant ready!")
    
    def listen_for_question(self):
        """Listen for user's question"""
        print("\n🎤 Listening... Ask your question now!")
        self.tts.speak_immediate("I'm listening. Ask your question now.")
        
        try:
            with self.microphone as source:
                # Listen for longer audio with higher timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=10,  # Wait up to 10 seconds for speech to start
                    phrase_time_limit=15  # Allow up to 15 seconds of speech
                )
            
            print("🧠 Processing your speech...")
            
            # Convert speech to text
            try:
                question = self.recognizer.recognize_google(audio)
                print(f"👤 You asked: {question}")
                return question
            except sr.UnknownValueError:
                print("❌ Could not understand the audio")
                self.tts.speak_immediate("Sorry, I couldn't understand what you said. Please try again.")
                return None
            except sr.RequestError as e:
                print(f"❌ Speech recognition error: {e}")
                self.tts.speak_immediate("Sorry, there was an error with speech recognition.")
                return None
                
        except sr.WaitTimeoutError:
            print("⏰ No speech detected")
            self.tts.speak_immediate("I didn't hear anything. Please try again.")
            return None
    
    def get_ai_response(self, question):
        """Get AI response from Gemini"""
        print("🧠 Getting AI response...")
        
        # Simple prompt for visually impaired users
        prompt = f"""You are a helpful AI assistant for visually impaired users. 
        
        The user asked: "{question}"
        
        Provide a clear, helpful response in 2-3 sentences. Be conversational and supportive.
        Avoid visual references unless specifically asked. Focus on practical, useful information.
        
        Response:"""
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'X-goog-api-key': config.GEMINI_API_KEY
            }
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 100,
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
                print(f"❌ AI API error: {response.status_code}")
                return "Sorry, I'm having trouble connecting to my AI brain right now."
                
        except Exception as e:
            print(f"❌ AI response error: {e}")
            return "Sorry, I encountered an error while thinking about your question."
    
    def speak_response(self, response):
        """Speak the AI response"""
        print(f"🤖 Assistant: {response}")
        self.tts.speak_immediate(response)
        
        # Wait for speech to complete
        time.sleep(len(response.split()) * 0.5)
    
    def run_conversation(self):
        """Run one conversation cycle"""
        # Listen for question
        question = self.listen_for_question()
        
        if question:
            # Check if user wants to exit
            if any(word in question.lower() for word in ['goodbye', 'exit', 'quit', 'stop']):
                self.tts.speak_immediate("Goodbye! Have a great day!")
                return False
            
            # Get AI response
            response = self.get_ai_response(question)
            
            # Speak response
            self.speak_response(response)
            
            return True
        
        return True
    
    def start(self):
        """Start the voice assistant"""
        print("🚀 Starting Simple Voice Assistant")
        print("=" * 50)
        
        # Welcome message
        welcome = "Hello! I'm your voice assistant. I'll listen to your questions and respond. Say goodbye when you want to stop."
        print(f"🤖 {welcome}")
        self.tts.speak_immediate(welcome)
        
        time.sleep(3)
        
        # Main conversation loop
        try:
            while True:
                if not self.run_conversation():
                    break
                
                # Small pause between conversations
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.tts.shutdown()
            print("✅ Voice assistant stopped")

def main():
    """Main function"""
    assistant = SimpleVoiceAssistant()
    assistant.start()

if __name__ == "__main__":
    main()