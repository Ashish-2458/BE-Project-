"""
Gemini AI client for image description
"""
import requests
import json
import time
from typing import Optional
import config

class GeminiClient:
    """Client for Gemini AI image description service"""
    
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        self.api_url = config.GEMINI_API_URL
        self.headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.api_key
        }
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Rate limiting
        
    def describe_image(self, image_base64: str) -> Optional[str]:
        """
        Send image to Gemini and get description
        
        Args:
            image_base64: Base64 encoded image string
            
        Returns:
            Description string or None if failed
        """
        try:
            # Rate limiting
            self._rate_limit()
            
            # Create prompt for blind person's perspective
            prompt = """You are helping a blind person navigate. This image is what they would see through their eyes if they could see. 

Provide a clear description (3-4 sentences, about 10-12 seconds to speak) from their perspective:

IMPORTANT: Describe what's in THEIR view as they move:
- Any immediate dangers or obstacles they need to avoid
- People nearby and exactly where (left, right, ahead, behind)
- Important objects and furniture in their path
- Doors, walls, stairs, or openings they're approaching
- Distance of objects (very close, close, medium, far)

Use their perspective: "directly in front of you", "to your left", "on your right", "behind you".
Be helpful and specific for safe navigation.

Describe what you see through their eyes:"""

            # Prepare API payload
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            },
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": image_base64
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 80,  # Slightly longer responses (10-12 seconds)
                    "topP": 0.8,
                    "topK": 20
                }
            }
            
            print("🧠 Sending image to Gemini AI...")
            
            # Make API request
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    description = result['candidates'][0]['content']['parts'][0]['text']
                    print("✅ Received AI description")
                    return description.strip()
                else:
                    print("❌ No description in API response")
                    return None
            else:
                print(f"❌ Gemini API error: {response.status_code}")
                if response.status_code == 429:
                    print("Rate limit exceeded, waiting...")
                    time.sleep(2)
                return None
                
        except requests.exceptions.Timeout:
            print("❌ API request timeout")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - check internet connection")
            return None
        except Exception as e:
            print(f"❌ Gemini client error: {e}")
            return None
    
    def _rate_limit(self):
        """Ensure minimum time between API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            print(f"⏳ Rate limiting: waiting {sleep_time:.1f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def test_connection(self) -> bool:
        """Test if API connection is working"""
        try:
            # Simple text-only test
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": "Say 'API connection successful' if you can read this."
                            }
                        ]
                    }
                ]
            }
            
            print("🧠 Testing API connection...")
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ API connection test passed")
                return True
            else:
                print(f"❌ API connection test failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
            
        except Exception as e:
            print(f"❌ API connection test failed: {e}")
            return False