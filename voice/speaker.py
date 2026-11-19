"""
Text-to-Speech Engine for JARVIS.
Uses Windows native SAPI via win32com for ultra-fast, zero-dependency, local voice synthesis.
Supports background speech queue, interrupt/stop, and rate/volume controls.
"""

import queue
import threading
import time
from typing import List, Optional
import pythoncom
import win32com.client


class VoiceSpeaker:
    def __init__(self, rate: int = 1, volume: int = 100):
        self.rate = rate  # -10 to 10 for SAPI (1 is natural brisk British/English)
        self.volume = volume  # 0 to 100
        self._speech_queue: queue.Queue = queue.Queue()
        self._is_speaking = False
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._speech_loop, daemon=True)
        self._worker_thread.start()

    def _speech_loop(self) -> None:
        """Dedicated thread with COM initialized for SAPI voice output."""
        pythoncom.CoInitialize()
        try:
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Rate = self.rate
            speaker.Volume = self.volume

            while True:
                text = self._speech_queue.get()
                if text is None:
                    break

                self._stop_event.clear()
                self._is_speaking = True

                try:
                    # SVSFlagsAsync = 1, SVSFPurgeBeforeSpeak = 2
                    # We speak synchronously inside the worker thread so queue order is preserved
                    speaker.Speak(text, 0)
                except Exception as e:
                    print(f"[VoiceSpeaker] Speak error: {e}")
                finally:
                    self._is_speaking = False
                    self._speech_queue.task_done()
        finally:
            pythoncom.CoUninitialize()

    def speak(self, text: str, interrupt: bool = False) -> None:
        """Queue text to be spoken. If interrupt=True, clears pending speeches."""
        if not text or not text.strip():
            return
        
        # Strip code blocks or very long raw markdown URLs for clean vocalization
        cleaned_text = self._clean_for_speech(text)
        if not cleaned_text:
            return

        if interrupt:
            self.stop()

        self._speech_queue.put(cleaned_text)

    def stop(self) -> None:
        """Interrupt and clear currently queued speech."""
        while not self._speech_queue.empty():
            try:
                self._speech_queue.get_nowait()
                self._speech_queue.task_done()
            except Exception:
                break
        self._stop_event.set()

    def is_speaking(self) -> bool:
        return self._is_speaking

    def _clean_for_speech(self, text: str) -> str:
        """Clean markdown, code blocks, and URLs so JARVIS speaks naturally."""
        import re
        # Remove markdown code blocks ```...```
        text = re.sub(r'```[\s\S]*?```', ' Code block omitted for brevity. ', text)
        # Remove inline backticks `code`
        text = re.sub(r'`([^`]+)`', r'\1', text)
        # Remove markdown links [title](url) -> title
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Remove raw URLs
        text = re.sub(r'https?://\S+', ' link ', text)
        # Clean up excess whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def get_available_voices(self) -> List[str]:
        voices = []
        try:
            pythoncom.CoInitialize()
            sp = win32com.client.Dispatch("SAPI.SpVoice")
            for v in sp.GetVoices():
                voices.append(v.GetDescription())
        except Exception:
            pass
        return voices


speaker = VoiceSpeaker()
