# Assistance Features

This folder contains additional assistance features for the AI vision system for visually impaired users.

## Structure
- Each feature will be developed independently in this folder


## Features

### 🎤 AI Voice Assistant (`voice_assistant/`)
An intelligent voice assistant specifically designed for visually impaired users.

**Features:**
- Voice-activated AI conversations with context awareness
- Accessibility-focused responses and interaction patterns
- Speech recognition with wake word detection
- Text-to-speech with queue management
- Conversation history and context memory
- Integration with Gemini AI for intelligent responses

**Usage:**
```bash
cd assistance/voice_assistant
python voice_assistant.py

python working_voice_assistant.py
```

**Wake words:** "hey assistant", "voice assistant", "help me"
**Exit commands:** "stop assistant", "goodbye", "exit"

**Components:**
- `voice_assistant.py` - Main assistant application
- `speech_recognition_handler.py` - Voice input processing
- `conversation_manager.py` - Context and history management
- `accessibility_prompts.py` - VI-specific prompts and responses
- `config.py` - Configuration settings
- `test_assistant.py` - Test suite for all components
