"""
Test script for fast speech system
"""
from simple_audio_system import SimpleAudioSystem
import time

def test_speech_speed():
    print("🎤 Testing Fast Speech System")
    print("=" * 40)
    
    # Initialize audio system
    audio = SimpleAudioSystem()
    if not audio.initialize():
        print("❌ Failed to initialize audio system")
        return
    
    # Test messages with different lengths
    test_messages = [
        "Person 3 meters ahead center",
        "ATTENTION: Obstacle 1 meter blocking path",
        "Chair 2.5 meters to your right, navigate left",
        "There's a person about 4.6 meters straight ahead in the center of your view",
        "Be aware, there's a person about 3 meters to your left, potentially blocking your path"
    ]
    
    print("\n🔊 Testing speech speed with different message lengths:")
    print("Rate set to 4 (fast but comfortable), Volume 90%")
    print("Minimum interval: 1.2 seconds")
    print()
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: {message[:50]}...")
        start_time = time.time()
        
        # Queue the message
        audio.speak_navigation(message, priority='normal')
        
        # Wait for speech to complete
        while audio.is_currently_speaking():
            time.sleep(0.1)
        
        duration = time.time() - start_time
        print(f"   ✅ Completed in {duration:.1f} seconds")
        print()
        
        # Small pause between tests
        time.sleep(1)
    
    # Test urgent priority
    print("🚨 Testing urgent priority (should interrupt):")
    audio.speak_navigation("This is a long message that should be interrupted", priority='normal')
    time.sleep(0.5)  # Let it start
    audio.speak_navigation("URGENT WARNING", priority='urgent')
    
    # Wait for completion
    time.sleep(3)
    
    # Test queue management
    print("\n📋 Testing queue management:")
    for i in range(5):
        audio.speak_navigation(f"Message number {i+1}", priority='normal')
    
    status = audio.get_queue_status()
    print(f"Queue status: {status}")
    
    # Wait for all to complete
    while audio.get_queue_status()['queue_size'] > 0 or audio.is_currently_speaking():
        time.sleep(0.1)
    
    # Shutdown
    audio.shutdown()
    print("\n✅ Speech speed test completed!")

if __name__ == "__main__":
    test_speech_speed()