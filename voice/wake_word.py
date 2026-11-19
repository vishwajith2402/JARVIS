"""
Wake Word and Hotkey Detector for JARVIS.
Detects activation triggers such as "Hey Jarvis" or global keyboard shortcuts.
"""

import re
from typing import Callable, Optional


class WakeWordDetector:
    def __init__(self, wake_words: Optional[list] = None):
        self.wake_words = wake_words or ["jarvis", "hey jarvis", "ok jarvis"]
        self._pattern = re.compile(
            r'\b(?:' + '|'.join(re.escape(w) for w in self.wake_words) + r')\b',
            re.IGNORECASE
        )

    def contains_wake_word(self, text: str) -> bool:
        if not text:
            return False
        return bool(self._pattern.search(text))

    def extract_command(self, text: str) -> str:
        """Strip the wake word from the input and return the actual command."""
        cleaned = self._pattern.sub("", text).strip()
        # Remove leading punctuation (e.g. ", please open code")
        cleaned = re.sub(r'^[,\.\s]+', '', cleaned)
        return cleaned


wake_detector = WakeWordDetector()
