"""
Voice Listener for JARVIS.
Captures spoken audio from the microphone and converts to text.
Supports ambient noise calibration, push-to-talk, and continuous listening.
"""

import threading
from typing import Callable, Optional
import speech_recognition as sr


class VoiceListener:
    def __init__(self, energy_threshold: int = 300, pause_threshold: float = 0.8):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = pause_threshold

        self._microphone: Optional[sr.Microphone] = None
        self._listening = False
        self._stop_listening_fn: Optional[Callable] = None
        self._callback: Optional[Callable[[str], None]] = None

    def _get_mic(self) -> Optional[sr.Microphone]:
        if self._microphone is None:
            try:
                self._microphone = sr.Microphone()
            except Exception as e:
                print(f"[VoiceListener] Microphone initialization error: {e}")
                return None
        return self._microphone

    def listen_once(self, timeout: float = 5.0, phrase_time_limit: float = 10.0) -> Optional[str]:
        """Record a single utterance and transcribe."""
        mic = self._get_mic()
        if not mic:
            return None

        try:
            with mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                text = self.recognizer.recognize_google(audio)
                return text.strip()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            print(f"[VoiceListener] Recognition error: {e}")
            return None

    def start_continuous_listening(self, callback: Callable[[str], None]) -> bool:
        """Start background thread listening continuously."""
        mic = self._get_mic()
        if not mic:
            return False

        self._callback = callback
        self._listening = True

        def _audio_callback(recognizer, audio):
            if not self._listening:
                return
            try:
                text = recognizer.recognize_google(audio)
                if text and self._callback:
                    self._callback(text.strip())
            except (sr.UnknownValueError, sr.RequestError):
                pass

        try:
            with mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self._stop_listening_fn = self.recognizer.listen_in_background(mic, _audio_callback)
            return True
        except Exception as e:
            print(f"[VoiceListener] Background listen error: {e}")
            return False

    def stop_continuous_listening(self) -> None:
        self._listening = False
        if self._stop_listening_fn:
            self._stop_listening_fn(wait_for_stop=False)
            self._stop_listening_fn = None


listener = VoiceListener()
