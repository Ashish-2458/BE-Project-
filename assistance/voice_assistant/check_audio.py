"""
Simple audio check
"""
import speech_recognition as sr

print("🎤 Simple Audio Check")
print("Available microphones:")

try:
    mics = sr.Microphone.list_microphone_names()
    for i, name in enumerate(mics[:3]):
        print(f"  {i}: {name}")
    
    print(f"\nTotal microphones found: {len(mics)}")
    
    if len(mics) > 0:
        print("✅ Microphones detected")
    else:
        print("❌ No microphones found")
        
except Exception as e:
    print(f"❌ Error: {e}")