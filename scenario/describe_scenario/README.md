# Describe Scenario Feature

## Overview
Continuous AI-powered environmental descriptions for visually impaired users with real-time updates.

## User Story
As a visually impaired user, I want detailed AI-powered descriptions of my surroundings with continuous real-time updates, so that I can understand what's around me as I move.

## Requirements
1. Automatically capture live image using device camera
2. Send image to Gemini AI model for analysis
3. Use text-to-speech to read AI description aloud
4. Enter real-time mode after first description
5. Continue describing environment every 10 seconds
6. Allow user to stop and return to main menu
7. Handle AI model errors gracefully

## Technical Implementation
- Camera capture with OpenCV
- Gemini 2.0 Flash API integration
- Text-to-speech with pyttsx3
- Real-time loop with 10-second intervals
- Error handling and fallbacks

## Files
- `main.py` - Main application entry point
- `camera_handler.py` - Camera capture functionality
- `gemini_client.py` - AI description service
- `speech_engine.py` - Text-to-speech handling
- `config.py` - Configuration settings
- `test_describe.py` - Testing script