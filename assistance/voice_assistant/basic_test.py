"""
Basic speech recognition test
"""
import speech_recognition as sr

def basic_test():
    print("🎤 Basic Speech Test")
    print("Say something when prompted...")
    
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = r.listen(source, timeout=5, phrase_time_limit=5)
    
    try:
        text = r.recognize_google(audio)
        print(f"You said: {text}")
    except:
        print("Could not understand")

if __name__ == "__main__":
    basic_test()