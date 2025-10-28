# 🎯 AI-Powered Assistive Vision System

An intelligent real-time vision system designed to help visually impaired individuals navigate their environment safely and independently.

## 🌟 Features

- **Real-time Object Detection**: Uses YOLOv8 for fast, accurate object recognition
- **Spatial Awareness**: Provides detailed position and distance information
- **Natural Language Descriptions**: Gemini AI generates contextual scene descriptions
- **Audio Feedback**: Clear text-to-speech navigation assistance
- **Smart Alerts**: Priority warnings for immediate obstacles and hazards
- **Adaptive Processing**: Intelligent scene change detection to minimize audio clutter

## 🏗️ System Architecture

```
📷 Webcam → 🔍 YOLO Detection → 🧠 Gemini AI → 🔊 Text-to-Speech
```

1. **Camera Module**: Captures continuous video feed with threading for smooth performance
2. **Object Detector**: YOLOv8-based detection with spatial analysis and distance estimation
3. **LLM Client**: Gemini API integration for intelligent scene interpretation
4. **Speech Engine**: Queue-managed text-to-speech with priority handling

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Webcam (built-in or USB)
- Internet connection (for Gemini API)

### Installation

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd assistive-vision
   python setup.py
   ```

2. **Run the system**:
   ```bash
   python main.py
   ```

### Manual Installation
```bash
pip install -r requirements.txt
python main.py
```

## 🎮 Usage

### Visual Mode (Development)
- Shows live video feed with object detection overlays
- Press `q` to quit
- Press `s` for system status
- Ideal for testing and demonstration

### Headless Mode (Production)
- No visual display, audio-only feedback
- Automatically selected when no display available
- Use `Ctrl+C` to stop
- Optimized for actual use by visually impaired users

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Camera settings
CAMERA_INDEX = 0          # Camera device index
FRAME_WIDTH = 640         # Video resolution
FRAME_HEIGHT = 480

# Detection settings
CONFIDENCE_THRESHOLD = 0.5  # Object detection confidence
DETECTION_INTERVAL = 2.0    # Seconds between detections

# Speech settings
SPEECH_RATE = 150          # Words per minute
SPEECH_VOLUME = 0.9        # Volume level (0.0-1.0)
```

## 🧠 AI Integration

### Gemini API
The system uses Google's Gemini 2.0 Flash model for:
- Scene interpretation and spatial reasoning
- Natural language description generation
- Context-aware navigation assistance

### Object Detection
YOLOv8 Nano model provides:
- Real-time object detection (30+ FPS)
- 80+ object classes (people, vehicles, furniture, etc.)
- Spatial position analysis (left/right/center, near/far)

## 🔊 Audio Feedback System

### Smart Descriptions
- **Scene Changes**: Describes environment when significant changes detected
- **Navigation Alerts**: Immediate warnings for close obstacles
- **Spatial Context**: "Person on your left", "Chair directly ahead"

### Priority System
- **Immediate Alerts**: Interrupt current speech for urgent warnings
- **Queue Management**: Prevents audio overlap and confusion
- **Rate Limiting**: Avoids overwhelming the user with information

## 📁 Project Structure

```
assistive-vision/
├── main.py              # Main application entry point
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── setup.py            # Installation script
├── README.md           # This file
└── modules/
    ├── __init__.py
    ├── camera.py       # Camera capture with threading
    ├── detector.py     # YOLO object detection
    ├── llm_client.py   # Gemini API integration
    └── speech.py       # Text-to-speech engine
```

## 🛠️ Technical Details

### Performance Optimizations
- **Threaded Camera**: Non-blocking video capture
- **Rate Limiting**: Prevents API overuse and reduces latency
- **Smart Processing**: Only processes frames when scene changes
- **Memory Efficient**: Optimized for continuous operation

### Accessibility Features
- **Clear Audio**: Optimized speech synthesis settings
- **Contextual Descriptions**: Focuses on navigation-relevant information
- **Interrupt Capability**: Urgent alerts override routine descriptions
- **Adaptive Timing**: Adjusts description frequency based on scene complexity

## 🔧 Troubleshooting

### Common Issues

**Camera not working**:
```bash
# Check camera permissions and availability
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

**Speech not working**:
- Windows: Should work out of the box
- macOS: Built-in speech synthesis
- Linux: Install espeak: `sudo apt-get install espeak`

**API errors**:
- Verify Gemini API key in `config.py`
- Check internet connection
- Monitor API usage limits

### Performance Tips
- Use lower resolution for better FPS: `FRAME_WIDTH = 320, FRAME_HEIGHT = 240`
- Increase detection interval for slower hardware: `DETECTION_INTERVAL = 3.0`
- Adjust confidence threshold to reduce false positives: `CONFIDENCE_THRESHOLD = 0.6`

## 🤝 Contributing

This project aims to improve accessibility through AI. Contributions welcome for:
- Performance optimizations
- Additional object classes
- Better spatial reasoning
- Multi-language support
- Mobile platform support

## 📄 License

MIT License - Feel free to use and modify for accessibility applications.

## 🙏 Acknowledgments

- **Ultralytics YOLOv8**: Fast, accurate object detection
- **Google Gemini**: Advanced language understanding
- **OpenCV**: Computer vision foundation
- **pyttsx3**: Cross-platform text-to-speech

---

*Built with ❤️ for accessibility and independence*


python main.py