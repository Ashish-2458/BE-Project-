"""
LLM integration for enhanced spatial descriptions using Gemini API
"""
import requests
import json
import time
from config import GEMINI_API_KEY, GEMINI_API_URL

class LLMIntegration:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.api_url = GEMINI_API_URL
        self.last_request_time = 0
        self.min_request_interval = 4.0  # 4 seconds between API calls (respects 15 req/min limit)
        self.api_call_count = 0
        
    def generate_spatial_description(self, navigation_summary):
        """
        Generate enhanced spatial description using Gemini
        """
        try:
            # Check if enough time has passed since last API call
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            # If not enough time, use fallback (no API call, no error message)
            if time_since_last < self.min_request_interval:
                return self._fallback_description(navigation_summary)
            
            # Create prompt from navigation data
            prompt = self._create_spatial_prompt(navigation_summary)
            
            # Call Gemini API
            response = self._call_gemini_api(prompt)
            
            if response:
                return response.strip()
            else:
                return self._fallback_description(navigation_summary)
                
        except Exception as e:
            # Silent fallback on errors
            return self._fallback_description(navigation_summary)
    
    def _create_spatial_prompt(self, summary):
        """Create concise prompt for spatial awareness"""
        top_objects = summary.get('top_objects', [])
        
        if not top_objects:
            return "Describe a clear path ahead."
        
        # Simplified prompt for faster responses
        prompt = "Navigation assistant: Describe obstacles briefly.\n\n"
        
        for i, obj in enumerate(top_objects[:3], 1):  # Only top 3 objects
            distance = obj.get('distance', 'unknown')
            location = obj.get('location_description', 'ahead')
            obj_class = obj.get('class', 'object')
            
            prompt += f"{obj_class} {distance}m {location}. "
        
        prompt += "\n\nGive 1 clear sentence for navigation:"
        
        return prompt
    
    def _call_gemini_api(self, prompt):
        """Call Gemini API with the spatial prompt"""
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.api_key
        }
        
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
                "temperature": 0.4,
                "maxOutputTokens": 60,  # Shorter, faster responses
                "topP": 0.9,
                "topK": 20
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=5  # Faster timeout
            )
            
            self.last_request_time = time.time()  # Update timestamp after request
            self.api_call_count += 1
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    return content
            elif response.status_code == 429:
                # Rate limited - silently use fallback (no error message)
                return None
            else:
                # Other errors - silent fallback
                return None
                
        except Exception as e:
            # Silent fallback on any error
            return None
            
        return None
    
    def _fallback_description(self, summary):
        """Generate fast fallback description without LLM"""
        top_objects = summary.get('top_objects', [])
        
        if not top_objects:
            return "Path clear."
        
        # Quick, simple descriptions
        obj = top_objects[0]  # Just the top object
        obj_class = obj.get('class', 'object')
        distance = obj.get('distance', 'unknown')
        location = obj.get('location_description', 'ahead')
        
        if isinstance(distance, (int, float)):
            distance_str = f"{distance:.1f} meters"
        else:
            distance_str = str(distance)
        
        return f"{obj_class} {distance_str} {location}. Navigate carefully."
    
    def generate_contextual_prompt(self, enhanced_detections):
        """Generate contextual information for general scene understanding"""
        if not enhanced_detections:
            return "Empty scene, no objects detected."
        
        # Count objects by category
        people_count = len([d for d in enhanced_detections if d['class'] == 'person'])
        furniture_count = len([d for d in enhanced_detections if d['class'] in ['chair', 'couch', 'bed', 'dining table']])
        vehicle_count = len([d for d in enhanced_detections if d['class'] in ['car', 'bicycle', 'motorcycle', 'bus', 'truck']])
        
        context_parts = []
        
        if people_count > 0:
            context_parts.append(f"{people_count} person(s)")
        if furniture_count > 0:
            context_parts.append(f"{furniture_count} furniture item(s)")
        if vehicle_count > 0:
            context_parts.append(f"{vehicle_count} vehicle(s)")
        
        if context_parts:
            return f"Scene contains: {', '.join(context_parts)}. Total {len(enhanced_detections)} objects detected."
        else:
            return f"{len(enhanced_detections)} objects detected in scene."