"""
Main AI Voice Assistant for Visually Impaired Users
"""
import sys
import os
import time
import threading
from typing import Optional

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import config
from speech_recognition_handler import SpeechRecognitionHandler
from conversation_manager import ConversationManager
from accessibility_prompts import get_context_aware_prompt, CONVERSATION_STARTERS, ERROR_RESPONSES
from OneVision.modules.speech import TextToSpeech

# Import Gemini client from scenario folder
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scenario', 'describe_scenario'))
from gemini_client import GeminiClient

class VoiceAssistant:
    """AI Voice Assistant specifically designed for visually impaired users"""
    
    def __init__(self):
        print("🤖 Initializing AI Voice Assistant for Visually Impaired Users...")
        
        # Initialize components
        self.conversation_manager = ConversationManager()
        self.tts = TextToSpeech(rate=config.TTS_RATE, volume=config.TTS_VOLUME)
        self.gemini_client = GeminiClient()
        
        # Initialize speech recognition
        self.speech_handler = SpeechRecognitionHandler(self._on_speech_received)
        
        self.is_running = False
        self.is_processing = False
        
        print("✅ Voice Assistant initialized successfully!")
    
    def start(self):
        """Start the voice assistant"""
        if self.is_running:
            print("⚠️ Assistant is already running")
            return
        
        print("🚀 Starting AI Voice Assistant...")
        
        # Test components
        if not self._test_components():
            print("❌ Component tests failed. Please check your setup.")
            return
        
        self.is_running = True
        
        # Welcome message
        welcome_msg = CONVERSATION_STARTERS[0]
        self.tts.speak(welcome_msg, priority=True)
        print(f"🔊 {welcome_msg}")
        
        # Start listening
        self.speech_handler.start_listening()
        
        print("✅ Voice Assistant is now active!")
        print("💡 Say 'hey assistant' followed by your question")
        print("💡 Say 'stop assistant' or 'goodbye' to exit")
        
        # Keep main thread alive
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received")
            self.stop()
    
    def stop(self):
        """Stop the voice assistant"""
        if not self.is_running:
            return
        
        print("🛑 Stopping Voice Assistant...")
        self.is_running = False
        
        # Stop components
        self.speech_handler.stop_listening()
        
        # Goodbye message
        goodbye_msg = "Goodbye! Take care and feel free to ask me anything anytime."
        self.tts.speak_immediate(goodbye_msg)
        
        # Shutdown
        time.sleep(2)  # Wait for goodbye message
        self.tts.shutdown()
        
        print("✅ Voice Assistant stopped")
    
    def _on_speech_received(self, user_input: str):
        """Handle speech input from user"""
        if not self.is_running or self.is_processing:
            return
        
        # Check for exit commands
        if self._is_exit_command(user_input):
            self.stop()
            return
        
        # Process the user's question
        self._process_user_question(user_input)
    
    def _process_user_question(self, user_input: str):
        """Process user question and generate AI response"""
        if not user_input.strip():
            return
        
        self.is_processing = True
        
        try:
            print(f"🤔 Processing: {user_input}")
            
            # Get conversation context
            conversation_history = self.conversation_manager.get_conversation_context()
            
            # Generate context-aware prompt
            prompt = get_context_aware_prompt(conversation_history, user_input)
            
            # Get AI response
            print("🧠 Getting AI response...")
            ai_response = self._get_ai_response(prompt)
            
            if ai_response:
                # Clean and optimize response for speech
                cleaned_response = self._clean_response_for_speech(ai_response)
                
                # Speak the response
                print(f"🔊 Response: {cleaned_response}")
                self.tts.speak(cleaned_response, priority=True)
                
                # Add to conversation history
                self.conversation_manager.add_exchange(user_input, cleaned_response)
                
            else:
                # Error response
                error_msg = ERROR_RESPONSES[0]
                self.tts.speak(error_msg, priority=True)
                print(f"❌ {error_msg}")
        
        except Exception as e:
            print(f"❌ Error processing question: {e}")
            error_msg = "I'm sorry, I encountered an error. Please try asking again."
            self.tts.speak(error_msg, priority=True)
        
        finally:
            self.is_processing = False
    
    def _get_ai_response(self, prompt: str) -> Optional[str]:
        """Get response from AI using Gemini"""
        try:
            # Create a simple text payload for Gemini
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
                    "maxOutputTokens": config.RESPONSE_MAX_LENGTH,
                    "topP": 0.8,
                    "topK": 20
                }
            }
            
            import requests
            response = requests.post(
                self.gemini_client.api_url,
                headers=self.gemini_client.headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    ai_response = result['candidates'][0]['content']['parts'][0]['text']
                    return ai_response.strip()
            else:
                print(f"❌ AI API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ AI response error: {e}")
            return None
    
    def _clean_response_for_speech(self, response: str) -> str:
        """Clean AI response for better speech synthesis"""
        # Remove markdown formatting
        response = response.replace('**', '').replace('*', '')
        response = response.replace('##', '').replace('#', '')
        
        # Replace common abbreviations
        replacements = {
            'e.g.': 'for example',
            'i.e.': 'that is',
            'etc.': 'and so on',
            'vs.': 'versus',
            '&': 'and',
            '@': 'at',
            '%': 'percent'
        }
        
        for old, new in replacements.items():
            response = response.replace(old, new)
        
        # Limit length for speech
        words = response.split()
        if len(words) > config.RESPONSE_MAX_LENGTH:
            response = ' '.join(words[:config.RESPONSE_MAX_LENGTH]) + "... Would you like me to continue?"
        
        return response.strip()
    
    def _is_exit_command(self, text: str) -> bool:
        """Check if user wants to exit"""
        exit_phrases = [
            "stop assistant", "goodbye", "exit", "quit", 
            "stop listening", "turn off", "shut down"
        ]
        
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in exit_phrases)
    
    def _test_components(self) -> bool:
        """Test all components before starting"""
        print("🧪 Testing components...")
        
        # Test TTS
        try:
            self.tts.speak_immediate("Testing voice output")
            print("✅ Text-to-speech working")
        except Exception as e:
            print(f"❌ TTS test failed: {e}")
            return False
        
        # Test microphone
        if not self.speech_handler.test_microphone():
            print("❌ Microphone test failed")
            return False
        
        # Test AI connection
        if not self.gemini_client.test_connection():
            print("❌ AI connection test failed")
            return False
        
        print("✅ All components working!")
        return True
    
    def get_stats(self):
        """Get assistant statistics"""
        stats = self.conversation_manager.get_session_stats()
        stats_msg = f"Session statistics: {stats['exchanges']} conversations, "
        stats_msg += f"running for {stats['session_duration']:.1f} seconds"
        
        print(stats_msg)
        self.tts.speak(stats_msg)
        
        return stats

def main():
    """Main function to run the voice assistant"""
    print("🤖 AI Voice Assistant for Visually Impaired Users")
    print("=" * 60)
    
    assistant = VoiceAssistant()
    
    try:
        assistant.start()
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        assistant.stop()

if __name__ == "__main__":
    main()