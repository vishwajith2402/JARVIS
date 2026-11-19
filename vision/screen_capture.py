"""
Screen Capture Module for JARVIS.
Captures screen, window, or display regions with automatic resizing to conserve VRAM.
"""

import time
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageGrab
from config.config_manager import config

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOT_DIR = PROJECT_ROOT / "data" / "screenshots"
try:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass


class ScreenCapturer:
    def __init__(self):
        self.max_dimension = config.get("vision", "max_image_dimension", 1024)

    def capture_fullscreen(self, save: bool = True) -> Tuple[Image.Image, Optional[str]]:
        """Capture entire desktop screen."""
        screenshot = ImageGrab.grab(all_screens=True)
        return self._process_and_save(screenshot, "fullscreen", save)

    def capture_region(self, bbox: Tuple[int, int, int, int], save: bool = True) -> Tuple[Image.Image, Optional[str]]:
        """Capture a bounding box (left, top, right, bottom)."""
        screenshot = ImageGrab.grab(bbox=bbox)
        return self._process_and_save(screenshot, "region", save)

    def _process_and_save(self, img: Image.Image, prefix: str, save: bool) -> Tuple[Image.Image, Optional[str]]:
        # Resize if image exceeds max dimension to keep VRAM usage low for RTX 3050
        w, h = img.size
        if max(w, h) > self.max_dimension:
            scale = self.max_dimension / max(w, h)
            new_w, new_h = int(w * scale), int(h * scale)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        file_path = None
        if save:
            filename = f"{prefix}_{int(time.time())}.png"
            dest = SCREENSHOT_DIR / filename
            img.save(dest, format="PNG")
            file_path = str(dest.resolve())

        return img, file_path


screen_capturer = ScreenCapturer()
