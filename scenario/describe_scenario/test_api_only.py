"""
Test API connection only
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gemini_client import GeminiClient

def test_api():
    print("🧪 Testing Gemini API...")
    
    client = GeminiClient()
    
    # Test connection
    print("Testing API connection...")
    if client.test_connection():
        print("✅ API connection successful")
    else:
        print("❌ API connection failed")
        
    # Test with simple text
    print("Testing text generation...")
    try:
        import requests
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": "Say 'Hello, API is working' if you can read this."
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(
            client.api_url,
            headers=client.headers,
            json=payload,
            timeout=10
        )
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ API test error: {e}")

if __name__ == "__main__":
    test_api()