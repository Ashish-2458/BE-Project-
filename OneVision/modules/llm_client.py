"""
Gemini API client - smart navigation descriptions with rate limiting
"""
import requests
import time
from typing import List, Dict, Optional

class GeminiClient:
    def __init__(self, api_key: str, api_url: str):
        self.api_key  = api_key
        self.api_url  = api_url
        self.headers  = {"Content-Type": "application/json",
                         "X-goog-api-key": api_key}
        self.last_call   = 0
        self.min_interval = 4.0   # 15 req/min free tier
        self.call_count  = 0

    # ------------------------------------------------------------------ #
    def describe_scene(self, detections: List[Dict],
                       path_guidance: str = "") -> str:
        """
        Returns a spoken navigation sentence.
        Uses Gemini if rate allows, otherwise fast local fallback.
        """
        now = time.time()
        if now - self.last_call < self.min_interval:
            return self._fallback(detections, path_guidance)

        try:
            det_text = self._fmt(detections)
            path_txt = f"\nPath status: {path_guidance}" if path_guidance else ""

            prompt = (
                "You are a navigation assistant for a blind person. "
                "Give ONE short spoken sentence (max 15 words) describing "
                "the most important obstacle and direction to move safely.\n\n"
                f"Detected: {det_text}{path_txt}\n\n"
                "Response (1 sentence only):"
            )

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 50,
                    "topP": 0.9,
                    "topK": 20
                }
            }

            resp = requests.post(self.api_url, headers=self.headers,
                                 json=payload, timeout=5)
            self.last_call  = time.time()
            self.call_count += 1

            if resp.status_code == 200:
                cands = resp.json().get("candidates", [])
                if cands:
                    return cands[0]["content"]["parts"][0]["text"].strip()
            # 429 or other error → silent fallback
            return self._fallback(detections, path_guidance)

        except Exception:
            return self._fallback(detections, path_guidance)

    # ------------------------------------------------------------------ #
    def get_quick_description(self, detections: List[Dict],
                              path_guidance: str = "") -> str:
        """Instant local description, no API call."""
        return self._fallback(detections, path_guidance)

    # ------------------------------------------------------------------ #
    def _fmt(self, detections: List[Dict]) -> str:
        parts = []
        for d in detections[:4]:
            dm  = d.get("distance_meters")
            dst = f"{dm}m" if dm else d.get("distance", "?")
            parts.append(f"{d['class_name']} {dst} {d['position']}")
        return "; ".join(parts)

    def _fallback(self, detections: List[Dict], path_guidance: str = "") -> str:
        if not detections:
            base = "Path clear"
            return f"{base}. {path_guidance}." if path_guidance else f"{base}."

        # Sort by danger + proximity
        def priority(d):
            dm = d.get("distance_meters") or 99
            return (0 if d["is_danger"] else 1, dm)

        top = sorted(detections, key=priority)[:2]
        parts = []
        for d in top:
            dm  = d.get("distance_meters")
            dst = f"{dm} meters" if dm else d.get("distance", "nearby")
            parts.append(f"{d['class_name']} {dst} {d['position']}")

        desc = ". ".join(parts)
        if path_guidance and ("BLOCKED" in path_guidance or "Move" in path_guidance):
            desc += f". {path_guidance}"
        return desc + "."
