#!/usr/bin/env python3
"""
BlindNav - Proximity Navigation System for Visually Impaired
Like a car backup camera but for walking.

Features:
  - 5 proximity zones (far-left to far-right) with depth measurement
  - YOLO object detection with class names
  - Safe path arrow showing clearest direction to walk
  - Smart voice: danger interrupts, cooldowns prevent spam
  - Two-panel display: camera zones | depth heatmap
  - 100% local - no internet needed
"""

import cv2
import numpy as np
import torch
import threading
import queue
import time
import sys
from transformers import pipeline
from PIL import Image
from ultralytics import YOLO

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────────────────────────────────
CAMERA_INDEX     = 0
FRAME_W, FRAME_H = 640, 480

ZONE_DANGER  = 0.5   # metres - RED   stop immediately (very close only)
ZONE_WARN    = 1.5   # metres - ORANGE caution
ZONE_NOTICE  = 3.5   # metres - YELLOW be aware

SPEECH_CD = {"danger": 4.0, "warn": 6.0, "notice": 10.0, "clear": 12.0}

ZONES = [
    ("far left",  0.00, 0.20),
    ("left",      0.20, 0.40),
    ("center",    0.40, 0.60),
    ("right",     0.60, 0.80),
    ("far right", 0.80, 1.00),
]

ZONE_COL = {
    "danger": (0,   0,   255),
    "warn":   (0,   110, 255),
    "notice": (0,   210, 255),
    "clear":  (0,   210, 80),
}

# Objects YOLO should highlight loudly
HIGH_PRIORITY = {"person", "car", "truck", "bus", "motorcycle",
                 "bicycle", "dog", "cat", "chair", "dining table",
                 "stairs", "step"}


# ─────────────────────────────────────────────────────────────────────────────
#  DEPTH ENGINE
# ─────────────────────────────────────────────────────────────────────────────
class DepthEngine:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pipe   = None

    def load(self):
        print(f"📏 Loading Depth Anything V2 on {self.device}…")
        try:
            self.pipe = pipeline(
                task="depth-estimation",
                model="LiheYoung/depth-anything-small-hf",
                device=0 if self.device == "cuda" else -1
            )
            print("✅ Depth model ready")
            return True
        except Exception as e:
            print(f"⚠️  Depth model failed, using fallback: {e}")
            return False

    def estimate(self, frame: np.ndarray) -> np.ndarray:
        if self.pipe is None:
            return self._fallback(frame)
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out = self.pipe(Image.fromarray(rgb))
            dm  = np.array(out["depth"], dtype=np.float32)
            dm  = cv2.normalize(dm, None, 0, 255, cv2.NORM_MINMAX)
            return dm.astype(np.uint8)
        except Exception:
            return self._fallback(frame)

    def _fallback(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        gx   = cv2.Sobel(blur, cv2.CV_64F, 1, 0, ksize=3)
        gy   = cv2.Sobel(blur, cv2.CV_64F, 0, 1, ksize=3)
        dm   = cv2.normalize(np.sqrt(gx**2 + gy**2), None, 0, 255, cv2.NORM_MINMAX)
        return (255 - dm).astype(np.uint8)

    def to_meters(self, val: float) -> float:
        # val is 0-255 where higher = closer
        # Use a wider range so not everything looks "close"
        norm = (255 - val) / 255.0
        return round(0.2 + norm * 12.0, 1)  # 0.2m to 12.2m range


# ─────────────────────────────────────────────────────────────────────────────
#  YOLO DETECTOR
# ─────────────────────────────────────────────────────────────────────────────
class ObjectDetector:
    def __init__(self):
        self.model = None

    def load(self):
        print("🔍 Loading YOLO…")
        try:
            self.model = YOLO("yolov8n.pt")
            print("✅ YOLO ready")
            return True
        except Exception as e:
            print(f"⚠️  YOLO failed: {e}")
            return False

    def detect(self, frame: np.ndarray) -> list:
        if self.model is None:
            return []
        try:
            results = self.model(frame, conf=0.45, verbose=False)
            dets = []
            if results and results[0].boxes is not None:
                fw, fh = frame.shape[1], frame.shape[0]
                for box in results[0].boxes:
                    x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].cpu().numpy()]
                    conf  = float(box.conf[0])
                    name  = self.model.names[int(box.cls[0])]
                    cx    = (x1 + x2) // 2
                    zone_idx = min(int(cx / fw * 5), 4)
                    dets.append({
                        "name": name, "conf": conf,
                        "bbox": (x1, y1, x2, y2),
                        "zone_idx": zone_idx,
                        "high_priority": name in HIGH_PRIORITY,
                    })
            return dets
        except Exception:
            return []


# ─────────────────────────────────────────────────────────────────────────────
#  ZONE ANALYSER
# ─────────────────────────────────────────────────────────────────────────────
class ZoneAnalyser:
    def analyse(self, depth_map: np.ndarray, engine: DepthEngine) -> list:
        h, w  = depth_map.shape
        roi   = depth_map[int(h * 0.25):, :]   # ignore sky/ceiling

        zones = []
        for name, x0f, x1f in ZONES:
            x0  = int(x0f * w)
            x1  = int(x1f * w)
            col = roi[:, x0:x1]

            # 85th percentile - robust to noise, ignores ceiling/walls
            val    = float(np.percentile(col, 85))
            dist_m = engine.to_meters(val)

            level = ("danger" if dist_m <= ZONE_DANGER else
                     "warn"   if dist_m <= ZONE_WARN   else
                     "notice" if dist_m <= ZONE_NOTICE  else "clear")

            zones.append({"name": name, "distance_m": dist_m,
                          "level": level, "x0": x0, "x1": x1})
        return zones

    def safe_direction(self, zones: list) -> str:
        """Returns the name of the clearest zone to walk toward."""
        # Weight center zones higher (natural walking direction)
        weights = [0.6, 0.8, 1.0, 0.8, 0.6]
        best_score = -1
        best_name  = "center"
        for i, z in enumerate(zones):
            score = z["distance_m"] * weights[i]
            if score > best_score:
                best_score = score
                best_name  = z["name"]
        return best_name


# ─────────────────────────────────────────────────────────────────────────────
#  SPEECH ENGINE
# ─────────────────────────────────────────────────────────────────────────────
class SpeechEngine:
    MAX_Q = 3

    def __init__(self, rate=165, volume=1.0):
        self.rate   = rate
        self.volume = volume
        self._q     = queue.Queue()
        self._busy  = False
        self._run   = True
        self._sapi  = sys.platform == "win32"
        threading.Thread(target=self._worker, daemon=True).start()

    def say(self, text: str, urgent: bool = False):
        if urgent:
            # Flush queue for urgent messages
            while not self._q.empty():
                try: self._q.get_nowait()
                except queue.Empty: break
        else:
            while self._q.qsize() >= self.MAX_Q:
                try: self._q.get_nowait()
                except queue.Empty: break
        self._q.put(text)

    def say_now(self, text: str):
        """Blocking speak for startup/shutdown."""
        self._speak(text)

    def is_busy(self): return self._busy or not self._q.empty()

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
        if self._sapi:
            try:
                import win32com.client
                sp = win32com.client.Dispatch("SAPI.SpVoice")
                sp.Rate   = max(-2, min(3, (self.rate - 150) // 20))
                sp.Volume = int(self.volume * 100)
                sp.Speak(text)
                return
            except Exception: pass
        try:
            import pyttsx3
            e = pyttsx3.init()
            e.setProperty("rate",   self.rate)
            e.setProperty("volume", self.volume)
            e.say(text)
            e.runAndWait()
            del e
        except Exception as ex:
            print(f"TTS error: {ex}")

    def shutdown(self):
        self._run = False


# ─────────────────────────────────────────────────────────────────────────────
#  SPEECH SCHEDULER
# ─────────────────────────────────────────────────────────────────────────────
class SpeechScheduler:
    def __init__(self, tts: SpeechEngine):
        self.tts        = tts
        self._last      = {}
        self._prev_lvl  = {}
        self._last_safe = 0
        self._last_obj  = {}
        self._last_guide = 0

    def update(self, zones: list, detections: list, safe_dir: str):
        now = time.time()

        # Build a quick lookup: zone_name → zone
        zone_map = {z["name"]: z for z in zones}

        # ── 1. IMMEDIATE DANGER - tell them to stop AND where to go ──────
        danger_zones = [z for z in zones if z["level"] == "danger"]
        if danger_zones:
            dz = min(danger_zones, key=lambda x: x["distance_m"])
            cd = SPEECH_CD["danger"]
            if now - self._last.get("danger_alert", 0) >= cd:
                # Find escape direction
                escape = self._escape_direction(zones, dz["name"])
                if escape:
                    msg = (f"Stop! Obstacle {dz['distance_m']} meters "
                           f"{dz['name']}. Step {escape}.")
                else:
                    msg = f"Stop! Very close obstacle {dz['name']}. Do not move."
                self.tts.say(msg, urgent=True)
                self._last["danger_alert"] = now
                return

        # ── 2. High-priority YOLO objects with direction ──────────────────
        for det in detections:
            if det["high_priority"]:
                name     = det["name"]
                cd       = 4.0
                if now - self._last_obj.get(name, 0) >= cd:
                    zone_name = ZONES[det["zone_idx"]][0]
                    # Tell them to avoid it
                    avoid = self._escape_direction(zones, zone_name)
                    if avoid:
                        msg = f"{name} on your {zone_name}. Move {avoid}."
                    else:
                        msg = f"{name} ahead. Slow down."
                    self.tts.say(msg)
                    self._last_obj[name] = now
                    return

        # ── 3. ACTIVE NAVIGATION GUIDANCE (core feature) ─────────────────
        # Every 4 seconds give a positive walking instruction
        if now - self._last_guide >= 4.0:
            guide = self._navigation_instruction(zones, safe_dir)
            self.tts.say(guide)
            self._last_guide = now
            return

        # ── 4. Zone cleared - reassure ────────────────────────────────────
        for z in zones:
            prev = self._prev_lvl.get(z["name"], "clear")
            if prev in ("danger", "warn") and z["level"] == "clear":
                if now - self._last.get(z["name"] + "_clear", 0) >= 5.0:
                    self.tts.say(f"{z['name']} is now clear.")
                    self._last[z["name"] + "_clear"] = now

        for z in zones:
            self._prev_lvl[z["name"]] = z["level"]

    def _navigation_instruction(self, zones: list, safe_dir: str) -> str:
        """
        Generate a positive walking instruction like a GPS.
        Always tells WHERE to go, not just what's blocking.
        """
        zone_map   = {z["name"]: z for z in zones}
        center     = zone_map.get("center", {})
        left       = zone_map.get("left", {})
        right      = zone_map.get("right", {})
        far_left   = zone_map.get("far left", {})
        far_right  = zone_map.get("far right", {})

        center_dist = center.get("distance_m", 0)
        left_dist   = left.get("distance_m", 0)
        right_dist  = right.get("distance_m", 0)

        # All clear - walk straight
        if all(z["level"] == "clear" for z in zones):
            return "All clear. Walk straight ahead."

        # Center is clear and best
        if center.get("level") == "clear" and center_dist >= left_dist and center_dist >= right_dist:
            if center_dist > 5.0:
                return f"Path clear ahead. Walk straight, {center_dist} meters open."
            else:
                return f"Walk straight. {center_dist} meters ahead."

        # Center blocked, guide to best side
        if center.get("level") in ("danger", "warn"):
            if left_dist > right_dist and left.get("level") in ("clear", "notice"):
                return f"Obstacle ahead. Turn left. {left_dist} meters clear on left."
            elif right_dist > left_dist and right.get("level") in ("clear", "notice"):
                return f"Obstacle ahead. Turn right. {right_dist} meters clear on right."
            elif far_left.get("level") == "clear":
                return "Move to your far left. Path is clear there."
            elif far_right.get("level") == "clear":
                return "Move to your far right. Path is clear there."
            else:
                return "Path blocked ahead. Stop and wait."

        # Slight obstruction - nudge
        if left_dist > right_dist + 1.0:
            return f"Slight left. More space on left, {left_dist} meters."
        elif right_dist > left_dist + 1.0:
            return f"Slight right. More space on right, {right_dist} meters."

        # Default: tell them the safe direction
        sd = zone_map.get(safe_dir, {})
        dist = sd.get("distance_m", 0)
        if safe_dir == "center":
            return f"Walk straight. {dist} meters ahead."
        else:
            return f"Head {safe_dir}. {dist} meters clear."

    def _escape_direction(self, zones: list, blocked_zone: str) -> str:
        """Find the best direction to escape from a blocked zone."""
        zone_map = {z["name"]: z for z in zones}
        order    = ["far left", "left", "center", "right", "far right"]
        blocked_idx = next((i for i, z in enumerate(order) if z == blocked_zone), 2)

        # Check adjacent zones first, then farther ones
        candidates = sorted(
            range(len(order)),
            key=lambda i: (abs(i - blocked_idx), -zone_map.get(order[i], {}).get("distance_m", 0))
        )
        for i in candidates:
            z = zone_map.get(order[i])
            if z and z["level"] in ("clear", "notice") and order[i] != blocked_zone:
                return order[i]
        return ""


# ─────────────────────────────────────────────────────────────────────────────
#  VISUALISER
# ─────────────────────────────────────────────────────────────────────────────
class Visualiser:

    def build(self, frame, depth_map, zones, detections,
              safe_dir, tts_busy, fps) -> np.ndarray:
        left  = self._cam_panel(frame, zones, detections, safe_dir, tts_busy, fps)
        right = self._depth_panel(frame, depth_map, zones, safe_dir)
        lp = cv2.resize(left,  (480, 380))
        rp = cv2.resize(right, (480, 380))
        return cv2.hconcat([lp, rp])

    # ── Camera panel ──────────────────────────────────────────────────────
    def _cam_panel(self, frame, zones, detections, safe_dir, tts_busy, fps):
        p = frame.copy()
        h, w = p.shape[:2]

        # Zone overlays
        for z in zones:
            col   = ZONE_COL[z["level"]]
            alpha = 0.18 if z["level"] == "clear" else 0.38
            x0, x1 = z["x0"], z["x1"]
            ov = p.copy()
            cv2.rectangle(ov, (x0, 0), (x1, h), col, -1)
            cv2.addWeighted(ov, alpha, p, 1 - alpha, 0, p)
            cv2.rectangle(p, (x0, 0), (x1, h), col, 2)

            # Distance badge
            badge = f"{z['distance_m']}m"
            bx    = x0 + 4
            cv2.putText(p, z["name"], (bx, h - 38),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.34, (220, 220, 220), 1)
            cv2.putText(p, badge,     (bx, h - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, col, 2)

            # Pulsing danger border
            if z["level"] == "danger":
                cv2.rectangle(p, (x0 + 3, 3), (x1 - 3, h - 3), col, 5)

        # YOLO bounding boxes
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            col = (0, 0, 255) if det["high_priority"] else (0, 200, 200)
            cv2.rectangle(p, (x1, y1), (x2, y2), col, 2)
            lbl = f"{det['name']} {det['conf']:.0%}"
            (tw, th), _ = cv2.getTextSize(lbl, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            cv2.rectangle(p, (x1, y1 - th - 6), (x1 + tw + 4, y1), col, -1)
            cv2.putText(p, lbl, (x1 + 2, y1 - 3),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)

        # Safe path arrow
        self._draw_arrow(p, zones, safe_dir)

        # Title bar
        cv2.rectangle(p, (0, 0), (w, 34), (12, 12, 12), -1)
        spk = "🔊 SPEAKING" if tts_busy else "READY"
        cv2.putText(p, f"BLINDNAV  FPS:{fps:.1f}  {spk}",
                    (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 230, 230), 1)
        cv2.putText(p, "Q=quit  P=status",
                    (6, h - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (140, 140, 140), 1)
        return p

    def _draw_arrow(self, panel, zones, safe_dir):
        """Draw a large arrow pointing toward the safest direction."""
        h, w = panel.shape[:2]
        cy   = h // 2

        # Find safe zone x-center
        for z in zones:
            if z["name"] == safe_dir:
                cx = (z["x0"] + z["x1"]) // 2
                break
        else:
            cx = w // 2

        # Arrow from bottom-center toward safe zone
        src = (w // 2, h - 60)
        dst = (cx,     h // 2 + 20)
        col = (0, 255, 120)
        cv2.arrowedLine(panel, src, dst, col, 4, tipLength=0.3)
        cv2.putText(panel, "SAFE", (cx - 18, h // 2 + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, col, 2)

    # ── Depth panel ───────────────────────────────────────────────────────
    def _depth_panel(self, frame, depth_map, zones, safe_dir):
        h, w = frame.shape[:2]
        dm   = cv2.resize(depth_map, (w, h))
        p    = cv2.applyColorMap(dm, cv2.COLORMAP_INFERNO)

        for z in zones:
            col = ZONE_COL[z["level"]]
            cv2.rectangle(p, (z["x0"], 0), (z["x1"], h), col, 2)
            cv2.putText(p, f"{z['distance_m']}m",
                        (z["x0"] + 4, h - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 2)
            # Highlight safe zone
            if z["name"] == safe_dir:
                cv2.rectangle(p, (z["x0"] + 4, 38),
                              (z["x1"] - 4, h - 4), (0, 255, 120), 3)

        cv2.rectangle(p, (0, 0), (w, 34), (12, 12, 12), -1)
        cv2.putText(p, f"DEPTH MAP  |  Safe: {safe_dir.upper()}",
                    (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        return p


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
class BlindNav:

    def __init__(self):
        self.depth     = DepthEngine()
        self.yolo      = ObjectDetector()
        self.analyser  = ZoneAnalyser()
        self.tts       = SpeechEngine()
        self.scheduler = SpeechScheduler(self.tts)
        self.vis       = Visualiser()

        self._lock       = threading.Lock()
        self._frame      = None
        self._depth_map  = None
        self._zones      = []
        self._detections = []
        self._safe_dir   = "center"
        self._running    = False

        self.frame_count = 0
        self.start_time  = time.time()

    def initialize(self) -> bool:
        print("🚀 BlindNav initializing…")

        self.depth.load()
        self.yolo.load()

        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        if not self.cap.isOpened():
            print("❌ Camera failed"); return False
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_W)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        print("✅ All systems ready!")
        self.tts.say_now(
            "Blind navigator ready. "
            "I will guide you through five zones: "
            "far left, left, center, right, and far right. "
            "I will warn you about obstacles and tell you the safest direction to walk."
        )
        return True

    def _vision_loop(self):
        """Background thread: depth + YOLO + zone analysis."""
        while self._running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.05); continue

            depth_map  = self.depth.estimate(frame)
            zones      = self.analyser.analyse(depth_map, self.depth)
            detections = self.yolo.detect(frame)
            safe_dir   = self.analyser.safe_direction(zones)

            with self._lock:
                self._frame      = frame.copy()
                self._depth_map  = depth_map
                self._zones      = zones
                self._detections = detections
                self._safe_dir   = safe_dir

            self.scheduler.update(zones, detections, safe_dir)

    def run(self):
        self._running = True
        vt = threading.Thread(target=self._vision_loop, daemon=True)
        vt.start()

        cv2.namedWindow("BlindNav", cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow("BlindNav", 30, 30)
        print("👁️  Running  |  Q=quit  P=status")

        while self._running:
            with self._lock:
                frame      = self._frame
                depth_map  = self._depth_map
                zones      = list(self._zones)
                detections = list(self._detections)
                safe_dir   = self._safe_dir

            if frame is None or depth_map is None:
                time.sleep(0.01); continue

            fps = self.frame_count / max(time.time() - self.start_time, 0.001)
            display = self.vis.build(frame, depth_map, zones, detections,
                                     safe_dir, self.tts.is_busy(), fps)
            cv2.imshow("BlindNav", display)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("p"):
                self._status(zones)

            self.frame_count += 1

        self._running = False
        cv2.destroyAllWindows()
        self.tts.say_now("Navigator shutting down. Stay safe.")
        self.tts.shutdown()
        self.cap.release()
        print("✅ Stopped")

    def _status(self, zones):
        fps = self.frame_count / max(time.time() - self.start_time, 0.001)
        print(f"\n📊 FPS:{fps:.1f}  Safe:{self._safe_dir}")
        for z in zones:
            bar = "█" * int(z["distance_m"])
            print(f"  {z['name']:12s} {z['distance_m']:4.1f}m  {bar}  [{z['level'].upper()}]")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    nav = BlindNav()
    if nav.initialize():
        nav.run()
