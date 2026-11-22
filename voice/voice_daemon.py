"""
Hands-Free Voice Daemon for TITAN.
Continuously listens for wake-words ('Hey Titan', 'Titan', 'Hey Jarvis'),
processes commands through the local AI Brain, and speaks responses out loud.
100% Hands-Free & Local.
"""

import time
import threading
from typing import Callable, Optional

from voice.listener import listener
from voice.wake_word import wake_detector
from voice.speaker import speaker
from core.brain import brain


class HandsFreeVoiceDaemon:
    def __init__(self):
        self._is_active = False
        self._thread: Optional[threading.Thread] = None
        self.on_command_callback: Optional[Callable[[str, str], None]] = None

    def start(self, on_command: Optional[Callable[[str, str], None]] = None) -> bool:
        """Start hands-free background wake-word listening loop."""
        if self._is_active:
            return True

        self.on_command_callback = on_command
        self._is_active = True

        def _on_speech(raw_text: str):
            if not self._is_active or not raw_text:
                return

            if wake_detector.contains_wake_word(raw_text):
                cmd = wake_detector.extract_command(raw_text)
                if not cmd:
                    speaker.speak("Yes Sir, I am listening.", interrupt=True)
                    time.sleep(0.5)
                    followup = listener.listen_once(timeout=6.0)
                    if followup:
                        cmd = followup

                if cmd:
                    reply = brain.chat(cmd)
                    speaker.speak(reply, interrupt=True)
                    if self.on_command_callback:
                        self.on_command_callback(cmd, reply)

        success = listener.start_continuous_listening(_on_speech)
        if success:
            print("[VoiceDaemon] Hands-free wake-word listener is ONLINE ('Hey Titan' / 'Titan').")
        return success

    def stop(self) -> None:
        self._is_active = False
        listener.stop_continuous_listening()
        print("[VoiceDaemon] Hands-free voice listener stopped.")


voice_daemon = HandsFreeVoiceDaemon()
