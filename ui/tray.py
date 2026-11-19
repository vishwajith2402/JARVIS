"""
Background Voice Assistant & System Tray Daemon for JARVIS (Mode 2).
Runs silently in the Windows system tray, listens for wake word or hotkey,
and executes spoken or typed tasks.
"""

import sys
import threading
import time
from typing import Optional
from config.config_manager import config
from core.brain import brain
from voice.listener import listener
from voice.speaker import speaker
from voice.wake_word import wake_detector


class JarvisBackgroundDaemon:
    def __init__(self):
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self.wake_enabled = True

    def _voice_handler(self, phrase: str) -> None:
        if not phrase or not self.wake_enabled:
            return

        print(f"[JARVIS Background] Heard phrase: '{phrase}'")
        if wake_detector.contains_wake_word(phrase):
            command = wake_detector.extract_command(phrase)
            speaker.speak("Yes, Sir?", interrupt=True)

            if not command:
                # User just said "Hey Jarvis" - listen for follow up command
                command = listener.listen_once(timeout=4.0)

            if command:
                print(f"[JARVIS Background] Executing command: '{command}'")
                reply = brain.generate_response(command)
                speaker.speak(reply)

    def start(self) -> None:
        self.running = True
        speaker.speak(f"J.A.R.V.I.S. background protocols initiated, {config.get('system', 'user_title', 'Sir')}.")
        listener.start_continuous_listening(self._voice_handler)
        print("[JARVIS] Background daemon active. Listening for 'Hey Jarvis'...")

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        self.running = False
        listener.stop_continuous_listening()
        speaker.speak("J.A.R.V.I.S. background protocols standing down.")
        print("[JARVIS] Background daemon stopped.")


daemon = JarvisBackgroundDaemon()

if __name__ == "__main__":
    daemon.start()
