# Enhanced Vision Assistant with Spatial Awareness

A comprehensive vision assistance system that combines real-time object detection, depth estimation, and spatial audio feedback for enhanced navigation support.

## 🌟 Features

### Core Pipeline
- **📷 Real-time Camera Feed**: Continuous video capture and processing
- **🤖 YOLO Object Detection**: Identifies people, furniture, vehicles, and other objects
- **📏 Depth Estimation**: Uses Depth Anything V2 for accurate distance measurement
- **🧩 Intelligent Fusion**: Combines detection and depth data for spatial context
- **🧠 LLM Enhancement**: Gemini API generates natural navigation descriptions
- **🔊 Spatial Audio**: Text-to-speech with directional cues and priority handling

### Advanced Capabilities
- **Priority-based Navigation**: Immediate warnings for close obstacles
- **Spatial Context Awareness**: Understands object relationships and blocking paths
- **Distance Zones**: Categorizes objects by proximity (immediate, close, medium, far)
- **Location Descriptions**: Natural language positioning (center-left, upper-right, etc.)
- **Multi-threaded Processing**: Parallel detection and depth estimation for real-time performance

## 🚀 Quick Start

### Installation
```bash
cd finaldepth
pip install -r requirements.txt
```

### Run the System
```bash
python main_system.py
```

## 🎮 Controls

- **Q**: Quit the application
- **D**: Toggle depth visualization
- **S**: Stop current speech
- **C**: Clear speech queue

## 📊 System Architecture

```
📷 Camera Feed
    ↓
🔄 Parallel Processing:
├── 🤖 YOLO Detection (objects: person, chair, vehicle, etc.)
└── 📏 Depth Anything V2 (distance estimation)
    ↓
🧩 Fusion Module (combines object detection + depth data)
    ↓
🧠 Enhanced LLM Prompt:
- Object: "person"
- Location: "center-left of view"  
- Distance: "3 meters away"
- Spatial context: "blocking your path"
    ↓
🔊 Spatial Audio TTS:
- "Person 3 meters ahead, slightly to your left, blocking your path"
- Use directional audio cues
    ↓
👂 User Hears Enhanced Navigation Info
```

## ⚙️ Configuration

Edit `config.py` to customize:
- **Camera settings**: Resolution, FPS, camera index
- **Detection thresholds**: Confidence levels, object priorities
- **Audio settings**: Speech rate, volume, voice selection
- **Distance zones**: Customize proximity categories
- **API settings**: Gemini API configuration

## 🔧 Components

### CameraSystem (`camera_system.py`)
- Threaded video capture
- Configurable resolution and frame rate
- Automatic camera initialization

### YOLODetector (`yolo_detector.py`)
- Real-time object detection using YOLOv8
- Priority object classification
- Bounding box and confidence scoring

### DepthEstimator (`depth_estimator.py`)
- Depth Anything V2 integration
- Distance calculation for detected objects
- Depth map visualization

### FusionModule (`fusion_module.py`)
- Combines detection and depth data
- Spatial context generation
- Navigation priority scoring
- Location description mapping

### LLMIntegration (`llm_integration.py`)
- Gemini API integration
- Natural language spatial descriptions
- Contextual navigation instructions
- Fallback descriptions for offline use

### AudioSystem (`audio_system.py`)
- Priority-based speech queue
- Spatial audio cues
- Immediate warning system
- Background speech processing

## 🎯 Use Cases

- **Navigation Assistance**: Real-time obstacle detection and path guidance
- **Spatial Awareness**: Understanding object relationships and distances
- **Safety Alerts**: Immediate warnings for close obstacles or people
- **Scene Description**: Comprehensive environment understanding
- **Accessibility Support**: Audio-first interface for visually impaired users

## 🔊 Audio Feedback Examples

- **Immediate**: "ATTENTION: Person 1.2 meters ahead in center, blocking your path"
- **Navigation**: "Chair 2.5 meters to your right, table 4 meters ahead-left, path clear on left side"
- **Scene**: "3 people detected, 2 chairs nearby, navigate carefully around furniture"

## 📈 Performance

- **Real-time Processing**: ~10 FPS on modern hardware
- **Low Latency Audio**: <500ms from detection to speech
- **Parallel Architecture**: Simultaneous detection and depth estimation
- **Efficient Memory Usage**: Optimized for continuous operation

## 🛠️ Troubleshooting

### Camera Issues
- Check camera permissions and availability
- Verify camera index in config.py
- Ensure no other applications are using the camera

### Model Loading
- First run will download YOLO and Depth models automatically
- Ensure stable internet connection for initial setup
- Check available disk space (models ~500MB total)

### Audio Problems
- Verify TTS engine installation
- Check system audio settings and permissions
- Try different voice selections in audio_system.py

## 🔮 Future Enhancements

- **GPS Integration**: Outdoor navigation support
- **Voice Commands**: Interactive control system
- **Mobile App**: Smartphone companion interface
- **Cloud Processing**: Offload heavy computation
- **Multi-camera Support**: 360-degree awareness
- **Haptic Feedback**: Tactile navigation cues

## 📝 License

This project is open source and available under the MIT License.