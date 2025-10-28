import requests
import json
import time
from typing import List, Dict, Optional

class GeminiClient:
    """Gemini API client for scene interpretation and description"""
    
    def __init__(self, api_key: str, api_url: str):
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': api_key
        }
        self.last_request_time = 0
        self.min_request_interval = 0.5  # Faster API calls
        self.last_description = ""
        self.description_count = 0
        
    def describe_scene(self, detections: List[Dict]) -> str:
        """Generate natural scene description from detections"""
        try:
            self._rate_limit()
            
            if not detections:
                return "No objects detected in view."
            
            # Create detection summary
            detection_text = self._format_detections(detections)
            
            prompt = f"""You are an AI assistant helping a blind person navigate. Based on these object detections, provide a clear, concise description of what's in their view. 

IMPORTANT: Be direct and informative. Do NOT use phrases like "Okay, I'm here to help" or "Let me tell you". Just describe what you see.

Focus on:
1. Most important objects and their locations (use simple directions like "in front", "to your left", "to your right")
2. Any potential obstacles or safety concerns
3. Spatial relationships between objects
4. Keep it conversational but direct

Detections: {detection_text}

Provide a natural, direct description in 1-2 sentences:"""

            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.4,  # More consistent responses
                    "maxOutputTokens": 60,  # Shorter, faster responses
                    "topP": 0.9,
                    "topK": 20
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=5  # Faster timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    return content.strip()
                else:
                    return self._generate_fallback_description(detections)
            else:
                print(f"Gemini API error: {response.status_code}")
                return self._generate_fallback_description(detections)
                
        except Exception as e:
            print(f"Error generating scene description: {e}")
            return self._generate_fallback_description(detections)
    
    def _rate_limit(self):
        """Ensure minimum time between API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def _format_detections(self, detections: List[Dict]) -> str:
        """Format detections for the prompt"""
        formatted = []
        for detection in detections[:5]:  # Limit to top 5 objects
            obj_info = f"{detection['class_name']} ({detection['confidence']:.1f}%) at {detection['position']}"
            formatted.append(obj_info)
        return "; ".join(formatted)
    
    def _generate_fallback_description(self, detections: List[Dict]) -> str:
        """Generate simple fallback when API fails"""
        if not detections:
            return "Clear path ahead."
        
        # Count people first (highest priority)
        people = [d for d in detections if d['class_name'] == 'person']
        if people:
            person = people[0]
            if len(people) == 1:
                return f"Person {person['position']}. Navigate carefully."
            else:
                return f"{len(people)} people detected. Stay alert."
        
        # Other objects
        main_obj = detections[0]
        return f"{main_obj['class_name'].title()} {main_obj['position']}."
    
    def get_quick_description(self, detections: List[Dict]) -> str:
        """Generate quick description without API call for frequent updates"""
        if not detections:
            return "Path is clear."
        
        # Prioritize people
        people = [d for d in detections if d['class_name'] == 'person']
        furniture = [d for d in detections if d['class_name'] in ['chair', 'table', 'couch', 'bed']]
        vehicles = [d for d in detections if d['class_name'] in ['car', 'truck', 'bus', 'bicycle']]
        
        if people:
            person = people[0]
            distance_desc = "very close" if person['distance'] == 'very close' else "nearby"
            return f"Person {distance_desc}, {person['position']}."
        elif vehicles:
            vehicle = vehicles[0]
            return f"{vehicle['class_name'].title()} detected. Stay safe."
        elif furniture:
            item = furniture[0]
            return f"{item['class_name'].title()} {item['position']}. Navigate around."
        else:
            return f"{detections[0]['class_name'].title()} ahead."

