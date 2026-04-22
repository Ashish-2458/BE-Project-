#!/usr/bin/env python3
"""
VLM Navigator - Gemini Vision Navigation for Blind Persons
Sends live camera frames to Gemini Vision every 2.5 seconds.
Gemini SEES the actual image and gives real navigation instructions.
Falls back to SAPI/pyttsx3 if ElevenLabs key is invalid.
"""

import cv2
import base64
import threading
import queue
import time
import sys
import requests
import numpy as np
from io import BytesIO
from PIL import Image

# ── API KEYS ──────────────────────────────────────────────────────────────────
GEMINI_API_KEY     = "AIzaSyAFfnD2wOiRQE2RcIkgxh6UpS_eGP1FXjc"
ELEVENLABS_API_KEY = "sk_2799743a4284bea2bcbee9d1b681da3d8cb8f25028f04876"
ELEVENLABS_VOICE   = "iWNf11sz1GrUE4ppxTOL"
GEMINI_URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
              "gemini-2.0-flash:generateContent")

# ── CONFIG ────────────────────────────────────────────────────────────────────
CAMERA_INDEX  = 0
FRAME_W       = 640
FRAME_H       = 480
VLM_INTERVAL  = 2.5   # seconds between Gemini calls

NAV_PROMPT = (
    "You are a real-time navigation assistant for a blind person. "
    "Look at this image and give ONE short navigation instruction (max 12 words). "
    "Rules: "
    "Tell WHERE to walk: Walk straight / Turn left / Move right slightly. "
    "Mention obstacles only if blocking: Chair on right walk left. "
    "If clear: Path clear walk straight. "
    "If danger: Stop obstacle very close ahead. "
    "Be direct like a GPS. One sentence only."
)


# ── GEMINI VISION ─────────────────────────────────────────────────────────────
class GeminiVision:
    def __init__(self):
        self.headers = {"Content-Type": "application/json",
                        "X-goog-api-key": GEMINI_API_KEY}
        self.call_count = 0

    def describe(self, frame: np.ndarray) -> str:
        try:
            small = cv2.resize(frame, (480, 360))
            rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            buf   = BytesIO()
            Image.fromarray(rgb).save(buf, format="JPEG", quality=75)
            b64   = base64.b64encode(buf.getvalue()).decode()

            payload = {
                "contents": [{"parts": [
                    {"text": NAV_PROMPT},
                    {"inline_data": {"mime_type": "image/jpeg", "data": b64}}
                ]}],
                "generationConfig": {
                    "temperature": 0.2, "maxOutputTokens": 40, "topP": 0.8
                }
            }
            resp = requests.post(GEMINI_URL, headers=self.headers,
                                 json=payload, timeout=8)
            self.call_count += 1
            print(f"Gemini response: {resp.status_code}")

            if resp.status_code == 200:
                cands = resp.json().get("candidates", [])
                if cands:
                    text = cands[0]["content"]["parts"][0]["text"].strip()
                    return text.split("\n")[0].strip('"').strip()
            elif resp.status_code == 429:
                return None
            else:
                print(f"Gemini {resp.status_code}")
                return None
        except Exception as e:
            print(f"VLM error: {e}")
            return None


# ── SPEECH ENGINE ─────────────────────────────────────────────────────────────
class SpeechEngine:
    """Tries ElevenLabs first, auto-falls back to SAPI/pyttsx3."""

    def __init__(self):
        self._q       = queue.Queue()
        self._busy    = False
        self._run     = True
        self._use_el  = False  # ElevenLabs key invalid, use local TTS directly
        self._sapi    = sys.platform == "win32"
        threading.Thread(target=self._worker, daemon=True).start()
        print("🎙️  Speech engine ready")

    def say(self, text: str, urgent: bool = False):
        if urgent:
            while not self._q.empty():
                try: self._q.get_nowait()
                except queue.Empty: break
        else:
            while self._q.qsize() >= 2:
                try: self._q.get_nowait()
                except queue.Empty: break
        self._q.put(text)

    def say_now(self, text: str):
        self._speak(text)

    def is_busy(self):
        return self._busy or not self._q.empty()

    def _worker(self):
        while self._run:
            try:
                text = self._q.get(timeout=0.5)
                self._busy = True
                self._speak(text)
                self._busy = False
            except queue.Empty:
                continue

    def _speak(self, text: str):
        print(f"🔊 {text}")
        if self._use_el:
            try:
                url  = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE}"
                hdrs = {"xi-api-key": ELEVENLABS_API_KEY,
                        "Content-Type": "application/json"}
                body = {"text": text, "model_id": "eleven_turbo_v2",
                        "voice_settings": {"stability": 0.5,
                                           "similarity_boost": 0.8,
                                           "speed": 1.1}}
                resp = requests.post(url, headers=hdrs, json=body, timeout=10)
                if resp.status_code == 200:
                    self._play_mp3(resp.content)
                    return
                else:
                    print(f"ElevenLabs {resp.status_code} → switching to local TTS")
                    self._use_el = False
            except Exception:
                self._use_el = False

        self._local(text)

    def _play_mp3(self, data: bytes):
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(data); tmp = f.name
        try:
            if self._sapi:
                import win32com.client
                wmp = win32com.client.Dispatch("WMPlayer.OCX")
                wmp.URL = tmp
                wmp.controls.play()
                time.sleep(0.5)
                while wmp.playState == 3:
                    time.sleep(0.1)
                wmp.close()
            else:
                import subprocess
                subprocess.run(["mpg123", "-q", tmp],
                               capture_output=True, timeout=15)
        except Exception:
            self._local("")
        finally:
            try: os.unlink(tmp)
            except Exception: pass

    def _local(self, text: str):
        if not text:
            return
        if self._sapi:
            try:
                import win32com.client
                sp = win32com.client.Dispatch("SAPI.SpVoice")
                sp.Rate = 2; sp.Volume = 100
                sp.Speak(text); return
            except Exception: pass
        try:
            import pyttsx3
            e = pyttsx3.init()
            e.setProperty("rate", 170)
            e.setProperty("volume", 1.0)
            e.say(text); e.runAndWait(); del e
        except Exception as ex:
            print(f"TTS error: {ex}")

    def shutdown(self):
        self._run = False


# ── DISPLAY ───────────────────────────────────────────────────────────────────
class Display:
    def __init__(self):
        self._instruction = "Waiting for Gemini..."
        self._instr_time  = time.time()

    def update(self, text: str):
        self._instruction = text
        self._instr_time  = time.time()

    def build(self, frame, fps, tts_busy, call_count, next_in) -> np.ndarray:
        p = frame.copy()
        h, w = p.shape[:2]

        # Bottom text area
        ov = p.copy()
        cv2.rectangle(ov, (0, h - 110), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(ov, 0.65, p, 0.35, 0, p)

        # Instruction text (word-wrapped)
        words = self._instruction.split()
        lines, line = [], []
        for word in words:
            line.append(word)
            if len(" ".join(line)) > 40:
                lines.append(" ".join(line[:-1]))
                line = [word]
        if line:
            lines.append(" ".join(line))

        y = h - 95
        for ln in lines[:3]:
            cv2.putText(p, ln, (10, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 120), 2)
            y += 32

        # Top status bar
        cv2.rectangle(p, (0, 0), (w, 36), (12, 12, 12), -1)
        spk = "SPEAKING" if tts_busy else "READY"
        cv2.putText(p,
                    f"VLM NAV  FPS:{fps:.1f}  {spk}  "
                    f"API:{call_count}  Next:{next_in:.1f}s",
                    (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (0, 220, 220), 1)

        # Freshness bar
        age = time.time() - self._instr_time
        fresh = max(0.0, 1.0 - age / VLM_INTERVAL)
        bw = int(w * fresh)
        col = (0, 255, 0) if fresh > 0.5 else (0, 120, 255)
        cv2.rectangle(p, (0, 34), (bw, 38), col, -1)

        cv2.putText(p, "Q=quit",
                    (6, h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (140, 140, 140), 1)
        return p


# ── MAIN ──────────────────────────────────────────────────────────────────────
class VLMNavigator:
    def __init__(self):
        self.vlm     = GeminiVision()
        self.tts     = SpeechEngine()
        self.display = Display()

        self._lock         = threading.Lock()
        self._latest_frame = None
        self._running      = False
        self._last_call    = 0

        self.frame_count = 0
        self.start_time  = time.time()

    def initialize(self) -> bool:
        print("🚀 VLM Navigator initializing…")
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        if not self.cap.isOpened():
            print("❌ Camera failed"); return False
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_W)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        print("✅ Camera ready")
        self.display.update("Ready. Gemini Vision will guide you.")
        self.tts.say("Vision navigator ready. I will guide you where to walk.")
        return True

    def _vlm_loop(self):
        while self._running:
            now = time.time()
            if now - self._last_call < VLM_INTERVAL:
                time.sleep(0.05); continue

            with self._lock:
                frame = self._latest_frame

            if frame is None:
                time.sleep(0.05); continue

            print(f"📸 Sending frame to Gemini... (call #{self.vlm.call_count + 1})")
            instruction = self.vlm.describe(frame)
            self._last_call = time.time()

            if instruction:
                print(f"🧠 Gemini: {instruction}")
                self.display.update(instruction)
                is_urgent = any(w in instruction.lower()
                                for w in ["stop", "danger", "very close", "careful"])
                # Always speak - don't skip based on is_busy
                self.tts.say(instruction, urgent=is_urgent)

    def run(self):
        self._running = True
        threading.Thread(target=self._vlm_loop, daemon=True).start()

        cv2.namedWindow("VLM Navigator", cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow("VLM Navigator", 30, 30)
        print("👁️  Running  |  Q=quit")

        while self._running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01); continue

            with self._lock:
                self._latest_frame = frame.copy()

            fps    = self.frame_count / max(time.time() - self.start_time, 0.001)
            next_in = max(0.0, VLM_INTERVAL - (time.time() - self._last_call))

            disp = self.display.build(frame, fps, self.tts.is_busy(),
                                      self.vlm.call_count, next_in)
            cv2.imshow("VLM Navigator", disp)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            self.frame_count += 1

        self._running = False
        cv2.destroyAllWindows()
        self.tts.say_now("Navigator shutting down. Stay safe.")
        self.tts.shutdown()
        self.cap.release()
        print("✅ Stopped")


if __name__ == "__main__":
    nav = VLMNavigator()
    if nav.initialize():
        nav.run()
