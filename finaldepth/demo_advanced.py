"""
Demo script for Advanced Enhanced Vision Assistant
Shows the advanced visualization mode with 3D measurements
"""
from main_system import EnhancedVisionAssistant
import time

def main():
    print("🚀 Starting Advanced Enhanced Vision Assistant Demo")
    print("=" * 50)
    print("Features:")
    print("🎯 Advanced depth visualization with plasma colormap")
    print("📏 3D distance measurements with pixel values")
    print("🎨 Enhanced UI with corner markers and modern styling")
    print("⚡ Real-time FPS counter")
    print("🔊 Spatial audio navigation")
    print("=" * 50)
    print()
    
    print("Controls:")
    print("Q - Quit application")
    print("D - Toggle depth visualization")
    print("M - Toggle between Advanced/Basic modes")
    print("S - Stop current speech")
    print("C - Clear speech queue")
    print("T - Test speech system")
    print("R - Reset speech system")
    print()
    
    assistant = EnhancedVisionAssistant()
    
    # Force advanced mode
    assistant.advanced_mode = True
    
    try:
        print("🎬 Starting demo...")
        assistant.start()
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")
    finally:
        assistant.stop()
        print("🎬 Demo ended")

if __name__ == "__main__":
    main()