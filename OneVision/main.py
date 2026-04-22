#!/usr/bin/env python3
"""
OneVision - World-Class AI Assistive Navigation System
YOLO Object Detection + Depth Anything V2 + Floor Segmentation + Gemini AI
Built for visually impaired navigation assistance
"""

import cv2
import time
import signal
import sys
import numpy as np
from typing import List, Dict
import threading

from modules.camera      import CameraCapture
from modules.detector    import ObjectDetector
from modules.llm_client  import GeminiClient
from modules.speech      import TextToSpeech
from modules.depth       import DepthEstimator
from modules.segmentation import FloorSegmenter
import config

# ─────────────────────────────────────────────────────────────────────────────
PANEL_W, PANEL_H = 426, 320   # 3 × 426 = 1278 px  ← fits any 1366+ laptop
DANGER_DIST      = 1.5        # metres – triggers urgent speech
CLOSE_DIST       = 3.0        # metres – elevated priority
# ─────────────────────────────────────────────────────────────────────────────


class OneVision:
    """
    Main system.
    Architecture:
      • Camera thread  → always-fresh frames (modules/camera.py)
      • Vision thread  → YOLO + Depth + Seg in background (non-blocking display)
      • Display thread → main thread, 30 fps, reads cached results
      • Speech thread  → modules/speech.py worker
    """

    def __init__(self):
        # Components
        self.camera   = None
        self.detector = None
        self.depth    = None
        self.seg      = None
        self.llm      = None
        self.tts      = None
        self.running  = False

        # Shared vision results (vision thread writes, display thread reads)
        self._lock            = threading.Lock()
        self.res_detections   = []
        self.res_depth_map    = None
        self.res_seg_mask     = None
        self.res_direction    = {"left": 0, "center": 0, "right": 0}
        self.res_guidance     = "Initializing..."
        self.res_guidance_col = (255, 255, 255)

        # Speech state
        self.last_speech_time = 0
        self.prev_scene_key   = ""
        self.last_urgent_time = 0

        # Stats
        self.frame_count = 0
        self.start_time  = time.time()
        self.vision_fps  = 0.0

    # ──────────────────────────────────────────────────────────────────────
    #  INIT
    # ──────────────────────────────────────────────────────────────────────
    def initialize(self) -> bool:
        print("🚀 OneVision initializing…")
        try:
            print("📷 Camera…")
            self.camera = CameraCapture(config.CAMERA_INDEX,
                                        config.FRAME_WIDTH, config.FRAME_HEIGHT)
            if not self.camera.start():
                print("❌ Camera failed"); return False

            print("🔍 YOLO…")
            self.detector = ObjectDetector(config.YOLO_MODEL,
                                           config.CONFIDENCE_THRESHOLD)

            print("📏 Depth Anything V2…")
            self.depth = DepthEstimator()
            self.depth.initialize()

            print("🗺️  Floor segmentation…")
            self.seg = FloorSegmenter()
            if not self.seg.initialize():
                print("⚠️  Segmentation unavailable – continuing")

            print("🧠 Gemini API…")
            self.llm = GeminiClient(config.GEMINI_API_KEY, config.GEMINI_API_URL)

            print("🔊 TTS…")
            self.tts = TextToSpeech(rate=config.SPEECH_RATE,
                                    volume=config.SPEECH_VOLUME)

            print("✅ All systems ready!")
            self.tts.speak_immediate(
                "OneVision ready. Object detection, depth sensing, and floor navigation active."
            )
            return True

        except Exception as e:
            print(f"❌ Init error: {e}"); return False

    # ──────────────────────────────────────────────────────────────────────
    #  VISION THREAD  (runs in background)
    # ──────────────────────────────────────────────────────────────────────
    def _vision_loop(self):
        """Runs YOLO + Depth + Seg continuously in a background thread."""
        last_t = 0
        while self.running:
            now = time.time()
            if now - last_t < config.DETECTION_INTERVAL:
                time.sleep(0.01)
                continue
            last_t = now

            frame = self.camera.get_frame()
            if frame is None:
                time.sleep(0.05); continue

            t0 = time.time()

            # 1. YOLO
            detections = self.detector.detect_objects(frame)

            # 2. Depth
            depth_map = self.depth.estimate_depth(frame)
            for det in detections:
                dm = self.depth.get_distance(depth_map, det["bbox"])
                det["distance_meters"] = dm
                det["distance"] = f"{dm}m" if dm else det["distance"]

            # 3. Segmentation
            seg_mask  = None
            direction = {"left": 0, "center": 0, "right": 0}
            guidance  = "Path unknown"
            g_col     = (255, 255, 255)
            if self.seg.model is not None:
                seg      = self.seg.segment(frame)
                seg_mask = self.seg.get_floor_mask(seg)
                direction = self.seg.get_path_direction(seg_mask)
                guidance, g_col = self.seg.get_guidance(direction)

            # 4. Store results
            with self._lock:
                self.res_detections   = detections
                self.res_depth_map    = depth_map
                self.res_seg_mask     = seg_mask
                self.res_direction    = direction
                self.res_guidance     = guidance
                self.res_guidance_col = g_col

            self.vision_fps = 1.0 / max(time.time() - t0, 0.001)

            # 5. Speech
            self._handle_speech(detections, guidance)

    # ──────────────────────────────────────────────────────────────────────
    #  SPEECH LOGIC
    # ──────────────────────────────────────────────────────────────────────
    def _handle_speech(self, detections: List[Dict], guidance: str):
        now = time.time()

        # ── URGENT: object closer than DANGER_DIST ──────────────────────
        for det in detections:
            dm = det.get("distance_meters")
            if dm and dm < DANGER_DIST and det["is_danger"]:
                if now - self.last_urgent_time > 2.0:   # max 1 urgent per 2s
                    msg = (f"Warning! {det['class_name']} {dm} meters "
                           f"{det['position']}. Stop or move aside.")
                    self.tts.speak_urgent(msg)
                    self.last_urgent_time = now
                    self.last_speech_time = now
                    print(f"🚨 URGENT: {msg}")
                return

        # ── REGULAR: scene changed or 5s timeout ────────────────────────
        scene_key = self._scene_key(detections, guidance)
        changed   = (scene_key != self.prev_scene_key or
                     now - self.last_speech_time > 5.0)

        if changed and not self.tts.is_busy():
            desc = self.llm.describe_scene(detections, guidance)
            if desc:
                self.tts.speak(desc, priority=True)
                self.last_speech_time = now
                self.prev_scene_key   = scene_key
                print(f"🗣️  {desc}")

    def _scene_key(self, detections: List[Dict], guidance: str) -> str:
        parts = [f"{d['class_name']}_{d['position']}_{d.get('distance_meters','?')}"
                 for d in detections]
        return "|".join(sorted(parts)) + "|" + guidance

    # ──────────────────────────────────────────────────────────────────────
    #  DISPLAY PANELS
    # ──────────────────────────────────────────────────────────────────────
    def _panel_detection(self, frame, detections, fps) -> np.ndarray:
        p = self.detector.draw_detections(frame, detections)
        # Dark title bar
        cv2.rectangle(p, (0, 0), (p.shape[1], 34), (15, 15, 15), -1)
        spk = "🔊" if self.tts.is_busy() else "  "
        cv2.putText(p, f"DETECTION  Obj:{len(detections)}  FPS:{fps:.1f}  {spk}",
                    (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 230, 230), 1)
        cv2.putText(p, "Q=quit  D=depth  S=seg  P=status",
                    (6, p.shape[0] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (160, 160, 160), 1)
        return p

    def _panel_depth(self, depth_map, detections, shape) -> np.ndarray:
        h, w = shape[:2]
        p = cv2.applyColorMap(depth_map, cv2.COLORMAP_PLASMA)
        p = cv2.resize(p, (w, h))

        zone = {
            "imm":  (0,   0,   255),
            "close":(0,   120, 255),
            "med":  (0,   220, 255),
            "far":  (0,   255, 80),
        }
        for det in detections:
            x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
            dm = det.get("distance_meters")
            if dm is not None:
                col = (zone["imm"]   if dm < 1.5 else
                       zone["close"] if dm < 3.0 else
                       zone["med"]   if dm < 6.0 else zone["far"])
                lbl = f"{det['class_name']} {dm}m"
            else:
                col, lbl = (180, 180, 180), det["class_name"]

            cv2.rectangle(p, (x1, y1), (x2, y2), col, 2)
            (tw, th), _ = cv2.getTextSize(lbl, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 1)
            cv2.rectangle(p, (x1, y1 - th - 6), (x1 + tw + 4, y1), col, -1)
            cv2.putText(p, lbl, (x1 + 2, y1 - 3),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 0, 0), 1)

        cv2.rectangle(p, (0, 0), (w, 34), (15, 15, 15), -1)
        cv2.putText(p, "DEPTH MAP  |  Depth Anything V2",
                    (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        return p

    def _panel_seg(self, frame, seg_mask, direction, guidance, g_col) -> np.ndarray:
        if seg_mask is None:
            p = frame.copy()
            cv2.rectangle(p, (0, 0), (p.shape[1], 34), (15, 15, 15), -1)
            cv2.putText(p, "FLOOR SEG  |  Loading…",
                        (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 120, 120), 1)
            return p
        return self.seg.build_seg_panel(frame, seg_mask, direction, guidance, g_col)

    # ──────────────────────────────────────────────────────────────────────
    #  MAIN VISUAL LOOP
    # ──────────────────────────────────────────────────────────────────────
    def run_visual_mode(self):
        print("👁️  Visual mode  |  Q=quit  D=depth  S=seg  P=status")
        cv2.namedWindow("OneVision", cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow("OneVision", 30, 30)

        show_depth = True
        show_seg   = True

        # Start vision processing in background
        vt = threading.Thread(target=self._vision_loop, daemon=True)
        vt.start()

        while self.running:
            frame = self.camera.get_frame()
            if frame is None:
                time.sleep(0.01); continue

            # Snapshot shared results
            with self._lock:
                dets      = list(self.res_detections)
                depth_map = self.res_depth_map
                seg_mask  = self.res_seg_mask
                direction = self.res_direction.copy()
                guidance  = self.res_guidance
                g_col     = self.res_guidance_col

            fps = self.frame_count / max(time.time() - self.start_time, 0.001)

            try:
                panels = [self._panel_detection(frame, dets, fps)]
                if show_depth and depth_map is not None:
                    panels.append(self._panel_depth(depth_map, dets, frame.shape))
                if show_seg:
                    panels.append(self._panel_seg(frame, seg_mask,
                                                  direction, guidance, g_col))

                resized = [cv2.resize(p, (PANEL_W, PANEL_H)) for p in panels]
                display = cv2.hconcat(resized)
                cv2.imshow("OneVision", display)

            except Exception as e:
                print(f"❌ Display: {e}")
                cv2.imshow("OneVision", frame)

            key = cv2.waitKey(1) & 0xFF
            if   key == ord("q"): break
            elif key == ord("d"):
                show_depth = not show_depth
                print(f"Depth panel: {'ON' if show_depth else 'OFF'}")
            elif key == ord("s"):
                show_seg = not show_seg
                print(f"Seg panel: {'ON' if show_seg else 'OFF'}")
            elif key == ord("p"):
                self._status()

            self.frame_count += 1

        cv2.destroyAllWindows()

    def run_headless_mode(self):
        print("🎧 Headless mode  |  Ctrl+C to quit")
        vt = threading.Thread(target=self._vision_loop, daemon=True)
        vt.start()
        while self.running:
            time.sleep(0.1)

    # ──────────────────────────────────────────────────────────────────────
    #  STATUS / SHUTDOWN
    # ──────────────────────────────────────────────────────────────────────
    def _status(self):
        fps = self.frame_count / max(time.time() - self.start_time, 0.001)
        print(f"\n📊 FPS:{fps:.1f}  VisionFPS:{self.vision_fps:.1f}"
              f"  Objects:{len(self.res_detections)}"
              f"  Path:{self.res_guidance}"
              f"  Speech:{'busy' if self.tts.is_busy() else 'idle'}"
              f"  API calls:{self.llm.call_count}")

    def shutdown(self):
        print("\n🛑 Shutting down OneVision…")
        self.running = False
        if self.tts:
            self.tts.speak_immediate("System shutting down. Goodbye.")
            time.sleep(1.2)
            self.tts.shutdown()
        if self.camera:
            self.camera.stop()
        print("✅ Shutdown complete")


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
def signal_handler(signum, frame):
    print("\n🛑 Interrupt…")
    if "system" in globals():
        system.shutdown()
    sys.exit(0)


def main():
    global system
    signal.signal(signal.SIGINT, signal_handler)

    system = OneVision()
    if not system.initialize():
        print("❌ Failed to initialize"); return 1

    system.running = True
    try:
        import os
        if os.environ.get("DISPLAY") or sys.platform == "win32":
            system.run_visual_mode()
        else:
            system.run_headless_mode()
    except KeyboardInterrupt:
        pass
    finally:
        system.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
