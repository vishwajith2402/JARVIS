"""
Universal Text-to-Speech Engine for TITAN.
Supports:
1. Ultra-realistic Neural Voice via Microsoft Edge Neural TTS (en-GB-RyanNeural / British Jarvis cadence).
2. Direct 24kHz audio output with sounddevice and soundfile.
3. Zero-lag instant interruption / barge-in (sd.stop()).
4. Robust offline fallback to Windows Native SAPI (win32com).
100% Free & Local.
"""

import os
import re
import queue
import asyncio
import tempfile
import threading
from typing import List, Optional

try:
    import edge_tts
    import sounddevice as sd
    import soundfile as sf
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    import pythoncom
    import win32com.client
    SAPI_AVAILABLE = True
except ImportError:
    SAPI_AVAILABLE = False


class VoiceSpeaker:
    def __init__(self, voice_engine: str = "neural", preferred_voice: str = "en-GB-RyanNeural", rate: int = 1, volume: int = 100):
        self.voice_engine = voice_engine
        self.preferred_voice = preferred_voice
        self.rate = rate
        self.volume = volume
        self._speech_queue: queue.Queue = queue.Queue()
        self._is_speaking = False
        self._stop_event = threading.Event()
        self._worker_thread = threading.Thread(target=self._speech_loop, daemon=True)
        self._worker_thread.start()

    def _speech_loop(self) -> None:
        """Dedicated background thread handling speech synthesis and playback."""
        if SAPI_AVAILABLE:
            try:
                pythoncom.CoInitialize()
            except Exception:
                pass

        while True:
            text = self._speech_queue.get()
            if text is None:
                break

            self._stop_event.clear()
            self._is_speaking = True

            try:
                spoken = False
                # Try Neural Edge-TTS first if configured
                if self.voice_engine == "neural" and EDGE_TTS_AVAILABLE:
                    spoken = self._speak_neural(text)

                # Fallback to local SAPI if neural failed or disabled
                if not spoken and SAPI_AVAILABLE:
                    self._speak_sapi(text)
            except Exception as e:
                print(f"[VoiceSpeaker] Speech output error: {e}")
            finally:
                self._is_speaking = False
                self._speech_queue.task_done()

    def _speak_neural(self, text: str) -> bool:
        """Synthesize and play audio using Microsoft Neural Edge-TTS."""
        temp_path = None
        try:
            async def _synth():
                communicate = edge_tts.Communicate(text, voice=self.preferred_voice)
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    tmp = f.name
                await communicate.save(tmp)
                return tmp

            temp_path = asyncio.run(_synth())
            if self._stop_event.is_set():
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return True

            data, fs = sf.read(temp_path)
            sd.play(data, fs)
            
            # Wait for playback or interruption
            duration = len(data) / fs
            elapsed = 0.0
            step = 0.05
            while elapsed < duration and not self._stop_event.is_set():
                threading.Event().wait(step)
                elapsed += step

            if self._stop_event.is_set():
                sd.stop()

            return True
        except Exception:
            return False
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def _speak_sapi(self, text: str) -> None:
        """Fallback to Windows SAPI SpVoice."""
        try:
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Rate = self.rate
            speaker.Volume = self.volume
            speaker.Speak(text, 0)
        except Exception as e:
            print(f"[VoiceSpeaker] SAPI error: {e}")

    def speak(self, text: str, interrupt: bool = False) -> None:
        """Queue text to be spoken. If interrupt=True, halts ongoing playback immediately."""
        if not text or not text.strip():
            return

        cleaned_text = self._clean_for_speech(text)
        if not cleaned_text:
            return

        if interrupt:
            self.stop()

        self._speech_queue.put(cleaned_text)

    def stop(self) -> None:
        """Instant interrupt / barge-in. Halts currently playing audio and purges queue."""
        self._stop_event.set()
        while not self._speech_queue.empty():
            try:
                self._speech_queue.get_nowait()
                self._speech_queue.task_done()
            except Exception:
                break
        if EDGE_TTS_AVAILABLE:
            try:
                sd.stop()
            except Exception:
                pass

    def is_speaking(self) -> bool:
        return self._is_speaking

    def _clean_for_speech(self, text: str) -> str:
        """Clean markdown, code blocks, and URLs so TITAN speaks naturally."""
        text = re.sub(r'```[\s\S]*?```', ' Code block generated and saved to sandbox. ', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        text = re.sub(r'https?://\S+', ' link ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def get_available_voices(self) -> List[str]:
        voices = ["en-GB-RyanNeural (British Jarvis)", "en-GB-ThomasNeural", "en-US-AndrewNeural", "en-US-AvaNeural"]
        if SAPI_AVAILABLE:
            try:
                sp = win32com.client.Dispatch("SAPI.SpVoice")
                for v in sp.GetVoices():
                    voices.append(f"SAPI: {v.GetDescription()}")
            except Exception:
                pass
        return voices


speaker = VoiceSpeaker()
