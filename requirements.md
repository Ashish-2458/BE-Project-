# Requirements Document

## Introduction

CompleteVision is an AI-powered vision assistance system designed to help visually impaired users navigate and understand their environment. The system uses camera input, object detection, AI language processing, and text-to-speech to provide four core assistance modes: scenario description, reading help, navigation guidance, and interactive voice assistance.

## Requirements

### Requirement 1: System Interface and Menu Navigation

**User Story:** As a visually impaired user, I want to select from different assistance modes using simple button controls, so that I can get the specific type of help I need at any moment.

#### Acceptance Criteria

1. WHEN the system starts THEN the system SHALL announce the available modes and button assignments: "Press 1 for Scenario Description, Press 2 for Reading Help, Press 3 for Navigation Support, Press 4 for AI Voice Assistant"
2. WHEN the user presses button 1 THEN the system SHALL activate "Describe Scenario" mode
3. WHEN the user presses button 2 THEN the system SHALL activate "Reading Help" mode
4. WHEN the user presses button 3 THEN the system SHALL activate "Navigation Support" mode
5. WHEN the user presses button 4 THEN the system SHALL activate "AI Voice Assistant" mode
6. WHEN the user presses the menu/back button THEN the system SHALL return to the main menu from any mode
7. IF an invalid button is pressed THEN the system SHALL announce the correct button options

### Requirement 2: Scenario Description (Button 1)

**User Story:** As a visually impaired user, I want detailed AI-powered descriptions of my surroundings with continuous real-time updates, so that I can understand what's around me as I move.

#### Acceptance Criteria

1. WHEN "Describe Scenario" mode is selected THEN the system SHALL automatically capture a live image using the device camera
2. WHEN the image is captured THEN the system SHALL send it to an AI model (like Gemini) for analysis
3. WHEN the AI model returns a description THEN the system SHALL use text-to-speech to read aloud the AI's description
4. WHEN the first description is complete THEN the system SHALL automatically enter real-time mode and continuously capture frames every few seconds for live descriptions
5. WHEN in real-time mode THEN the system SHALL continue describing the environment every 10 seconds by capturing frames and providing AI-generated descriptions in speech 
6. WHEN the user presses the stop button THEN the system SHALL exit real-time mode and return to the main menu
7. IF the AI model is unavailable or returns an error THEN the system SHALL inform the user and suggest trying again

### Requirement 3: Reading Help (Button 2)

**User Story:** As a visually impaired user, I want text and signs read aloud to me, so that I can access written information in my environment.

#### Acceptance Criteria

1. WHEN "Reading Help" mode is selected THEN the system SHALL use OCR to detect and extract text from the camera feed
2. WHEN text is detected THEN the system SHALL read the text aloud using text-to-speech
3. WHEN the user presses the repeat button THEN the system SHALL re-read the last detected text
4. WHEN multiple text areas are detected THEN the system SHALL read them in logical order (top to bottom, left to right)
5. IF no text is detected THEN the system SHALL inform the user "no text found in view"

### Requirement 4: Navigation Support (Button 3)

**User Story:** As a visually impaired user, I want navigation guidance using AI-powered object detection, so that I can move safely and avoid obstacles.

#### Acceptance Criteria

1. WHEN "Navigation Support" mode is selected THEN the system SHALL continuously capture camera feed and process it through YOLO detection to identify objects such as person, chair, vehicle, etc.
2. WHEN YOLO detects objects in the camera feed THEN the system SHALL send the detection results to an LLM to convert them into natural, human-like navigation guidance text
3. WHEN the LLM generates navigation guidance THEN the system SHALL use text-to-speech to transform the output into spoken audio for the user to hear
4. WHEN obstacles are detected in the user's path THEN the system SHALL provide directional guidance like "obstacle ahead, move left" or "clear path straight ahead"
5. WHEN the user presses the scan button THEN the system SHALL perform immediate YOLO detection and provide LLM-generated descriptions of obstacles and safe directions
6. WHEN stairs, curbs, or elevation changes are detected THEN the system SHALL alert the user with specific warnings through the YOLO → LLM → TTS pipeline
7. IF the path is clear THEN the system SHALL confirm "path is clear" to reassure the user

### Requirement 5: AI Voice Assistant (Button 4)

**User Story:** As a visually impaired user, I want to have conversations with an AI assistant for both general questions and vision-specific help, so that I can get comprehensive assistance and interactive support.

#### Acceptance Criteria

1. WHEN "AI Voice Assistant" mode is selected THEN the system SHALL enable voice interaction and greet the user with "Hi! How is your day going? What can I help you with?"
2. WHEN the user asks general questions THEN the system SHALL provide general Q&A responses using LLM capabilities for any topic
3. WHEN the user speaks questions about their surroundings THEN the system SHALL analyze the camera feed and provide relevant answers
4. WHEN the user asks "what do you see" THEN the system SHALL provide a comprehensive description combining object detection and scene analysis
5. WHEN the user asks specific questions like "is there a chair nearby" THEN the system SHALL search for and report on specific objects using camera analysis
6. WHEN the user asks for help with tasks THEN the system SHALL provide step-by-step guidance based on visual analysis
7. WHEN the user engages in casual conversation THEN the system SHALL respond naturally while remaining ready to assist with vision-related queries

### Requirement 6: System Reliability and Controls

**User Story:** As a visually impaired user, I want the system to work reliably with button controls, so that I can operate it easily and consistently.

#### Acceptance Criteria

1. WHEN the system is running THEN it SHALL respond to button presses within 1 second
2. WHEN a button is pressed THEN the system SHALL provide immediate audio feedback confirming the action
3. WHEN the system is processing THEN it SHALL provide audio feedback like "processing" or "analyzing"
4. WHEN the exit button is pressed THEN the system SHALL safely shut down
5. IF a button press is not recognized THEN the system SHALL announce the available button options

### Requirement 7: LLM Integration with Gemini API

**User Story:** As a system developer, I want to integrate with Google's Gemini 2.0 Flash API for all AI language processing, so that the system can provide intelligent responses and descriptions.

#### Acceptance Criteria

1. WHEN the system needs LLM processing THEN it SHALL use the Gemini 2.0 Flash API endpoint: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`
2. WHEN making API calls THEN the system SHALL include the required headers: `Content-Type: application/json` and `X-goog-api-key: AIzaSyBBcYQyL8YJpzE1PkrJbTEcephbly1-BoU`
3. WHEN sending requests THEN the system SHALL format the payload as JSON with the structure: `{"contents": [{"parts": [{"text": "user_prompt_here"}]}]}`
4. WHEN the API returns a response THEN the system SHALL extract the generated text and process it for text-to-speech output
5. WHEN API calls fail THEN the system SHALL implement retry logic with exponential backoff
6. IF the API is unavailable THEN the system SHALL inform the user and suggest trying again later
7. WHEN processing images THEN the system SHALL include both image data and text prompts in the API request for vision-language tasks

### Requirement 8: Audio Feedback and User Experience

**User Story:** As a visually impaired user, I want clear audio feedback and instructions, so that I can understand how to use the system effectively.

#### Acceptance Criteria

1. WHEN the system starts THEN it SHALL announce "CompleteVision ready" and present the button menu options
2. WHEN switching between modes THEN the system SHALL announce the current mode
3. WHEN processing takes time THEN the system SHALL provide status updates like "analyzing image" or "generating description"
4. WHEN errors occur THEN the system SHALL explain the issue in simple terms and suggest solutions
5. IF the camera is not available THEN the system SHALL inform the user and provide troubleshooting guidance