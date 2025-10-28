"""
Text-based Voice Assistant (type questions, get spoken answers)
Perfect for testing without microphone issues
"""
import sys
import os
import time
import requests

# Add paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from OneVision.modules.speech import TextToSpeech
import config

class TextVoiceAssistant:
    """Voice assistant that takes text input and speaks responses"""
    
    def __init__(self):
        print("🤖 Initializing Text-to-Voice Assistant...")
        self.tts = TextToSpeech()
        print("✅ Assistant ready!")
    
    def get_ai_response(self, question):
        """Get AI response from Gemini"""
        print("🧠 Getting AI response...")
        
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
        print(f"\n🤖 Assistant: {response}")
        self.tts.speak_immediate(response)
        
        # Wait for speech to complete
        time.sleep(len(response.split()) * 0.6)
    
    def start(self):
        """Start the assistant"""
        print("🚀 Text-to-Voice Assistant")
        print("=" * 50)
        print("Type your questions and I'll speak the answers!")
        print("Type 'quit' or 'exit' to stop\n")
        
        # Welcome message
        welcome = "Hello! I'm your voice assistant. Type your questions and I'll speak the answers."
        self.tts.speak_immediate(welcome)
        time.sleep(3)
        
        try:
            while True:
                # Get text input
                question = input("\n💬 Your question: ").strip()
                
                if not question:
                    continue
                
                # Check for exit
                if question.lower() in ['quit', 'exit', 'goodbye', 'stop']:
                    goodbye = "Goodbye! Have a great day!"
                    print(f"🤖 {goodbye}")
                    self.tts.speak_immediate(goodbye)
                    time.sleep(2)
                    break
                
                # Get and speak AI response
                response = self.get_ai_response(question)
                self.speak_response(response)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.tts.shutdown()
            print("✅ Assistant stopped")

def main():
    """Main function"""
    assistant = TextVoiceAssistant()
    assistant.start()

if __name__ == "__main__":
    main()