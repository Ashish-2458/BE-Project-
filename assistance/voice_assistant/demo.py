"""
Demo script for AI Voice Assistant
Shows basic functionality without full voice recognition
"""
import sys
import os
import time

# Add paths
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

def demo_conversation():
    """Demo conversation without voice input"""
    print("🎤 AI Voice Assistant Demo")
    print("=" * 50)
    
    try:
        from conversation_manager import ConversationManager
        from accessibility_prompts import get_context_aware_prompt
        from OneVision.modules.speech import TextToSpeech
        import requests
        import config
        
        # Initialize components
        cm = ConversationManager()
        tts = TextToSpeech()
        
        # Demo questions
        demo_questions = [
            "What time is it?",
            "How can you help me as a visually impaired person?",
            "Tell me about the weather",
            "What are some tips for safe navigation?",
            "Can you help me with cooking?"
        ]
        
        print("🤖 Starting demo conversation...")
        tts.speak_immediate("Hello! I'm your AI voice assistant. Let me show you how I can help.")
        
        time.sleep(3)
        
        for i, question in enumerate(demo_questions, 1):
            print(f"\n--- Demo Question {i} ---")
            print(f"👤 User: {question}")
            
            # Get AI response
            conversation_history = cm.get_conversation_context()
            prompt = get_context_aware_prompt(conversation_history, question)
            
            # Call Gemini API
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
                    "maxOutputTokens": 150,
                    "topP": 0.8,
                    "topK": 20
                }
            }
            
            try:
                response = requests.post(
                    config.GEMINI_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # Clean response
                    ai_response = ai_response.replace('**', '').replace('*', '').strip()
                    
                    print(f"🤖 Assistant: {ai_response}")
                    
                    # Speak response
                    tts.speak(ai_response)
                    
                    # Add to conversation history
                    cm.add_exchange(question, ai_response)
                    
                    # Wait for speech to complete
                    time.sleep(len(ai_response.split()) * 0.4)  # Rough timing
                    
                else:
                    print(f"❌ API Error: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error getting AI response: {e}")
            
            time.sleep(1)
        
        print("\n🎉 Demo completed!")
        tts.speak_immediate("Demo completed! I'm ready to help you with any questions.")
        
        time.sleep(3)
        tts.shutdown()
        
        # Show conversation stats
        stats = cm.get_session_stats()
        print(f"\n📊 Session Stats: {stats['exchanges']} conversations")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def main():
    """Run the demo"""
    print("This demo shows the AI voice assistant responding to sample questions.")
    print("The assistant will speak each response out loud.")
    print("\nPress Ctrl+C to stop at any time.\n")
    
    try:
        demo_conversation()
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    main()