"""
Smart TTS engine - fast queue, urgent interrupt, Windows SAPI
"""
import threading
import queue
import time
import sys

class TextToSpeech:
    MAX_QUEUE = 3   # never pile up more than 3 items

    def __init__(self, rate: int = 160, volume: float = 1.0):
        self.rate   = rate
        self.volume = volume
        self._q     = queue.Queue()
        self._speaking = False
        self._running  = True

        # Windows SAPI check
        self._sapi = False
        if sys.platform == "win32":
            try:
                import win32com.client
                self._sapi = True
            except ImportError:
                pass

        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        print("🔊 Text-to-speech initialized")

    # ------------------------------------------------------------------ #
    def speak(self, text: str, priority: bool = False, interrupt: bool = False):
        """Queue speech. If interrupt=True, drop everything and speak now."""
        if not text or not text.strip():
            return
        text = text.strip()

        if interrupt:
            self._drain()

        # Drop oldest if queue full
        while self._q.qsize() >= self.MAX_QUEUE:
            try:
                self._q.get_nowait()
            except queue.Empty:
                break

        item = {"text": text, "ts": time.time(), "priority": priority}

        if priority and not interrupt:
            # Prepend: drain, put this first, re-add up to 1 old item
            old = []
            while not self._q.empty():
                try: old.append(self._q.get_nowait())
                except queue.Empty: break
            self._q.put(item)
            if old:
                self._q.put(old[-1])   # keep only the most recent old item
        else:
            self._q.put(item)

    def speak_urgent(self, text: str):
        """Interrupt everything and speak immediately (danger alerts)."""
        self._drain()
        self._q.put({"text": text.strip(), "ts": time.time(), "priority": True})

    def speak_immediate(self, text: str):
        """Blocking speak - used for startup/shutdown messages."""
        print(f"🔊 Immediate: {text}")
        self._drain()
        self._say(text)

    # ------------------------------------------------------------------ #
    def _worker(self):
        while self._running:
            try:
                item = self._q.get(timeout=0.5)
                self._speaking = True
                self._say(item["text"])
                self._speaking = False
            except queue.Empty:
                continue
            except Exception as e:
                self._speaking = False

    def _say(self, text: str):
        text = self._clean(text)
        print(f"🔊 Speaking: {text}")
        if self._sapi:
            try:
                import win32com.client
                sp = win32com.client.Dispatch("SAPI.SpVoice")
                sp.Rate   = max(-2, min(2, (self.rate - 150) // 25))
                sp.Volume = int(self.volume * 100)
                sp.Speak(text)
                return
            except Exception:
                pass
        # pyttsx3 fallback
        try:
            import pyttsx3
            eng = pyttsx3.init()
            eng.setProperty("rate",   self.rate)
            eng.setProperty("volume", self.volume)
            eng.say(text)
            eng.runAndWait()
            del eng
        except Exception as e:
            print(f"❌ TTS error: {e}")

    def _clean(self, text: str) -> str:
        text = " ".join(text.split())
        for k, v in {"w/": "with", "&": "and", "@": "at", "%": "percent"}.items():
            text = text.replace(k, v)
        return text

    def _drain(self):
        while not self._q.empty():
            try: self._q.get_nowait()
            except queue.Empty: break

    # ------------------------------------------------------------------ #
    def is_busy(self) -> bool:
        return self._speaking or not self._q.empty()

    def clear_queue(self):
        self._drain()

    def stop_current_speech(self):
        pass  # SAPI blocks; drain prevents future items

    def shutdown(self):
        self._running = False
        self._drain()
        self._thread.join(timeout=2.0)
        print("Text-to-speech shutdown")
