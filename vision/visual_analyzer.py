"""
Visual Analyzer for JARVIS.
Sends captured screens/images to local Ollama vision models (moondream / llama3.2-vision).
"""

import base64
import io
import json
import urllib.request
from typing import Any, Dict, Optional
from PIL import Image
from config.config_manager import config
from vision.screen_capture import screen_capturer


class VisualAnalyzer:
    def __init__(self):
        self.ollama_url = config.get("ai", "ollama_url", "http://127.0.0.1:11434")
        self.vision_model = config.get("ai", "vision_model", "moondream:latest")

    def _image_to_base64(self, image: Image.Image) -> str:
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def analyze_screen(self, prompt: str = "Describe what is on this screen, specifically any code, errors, or open applications.") -> Dict[str, Any]:
        """Capture the current screen and ask the vision model to analyze it."""
        img, path = screen_capturer.capture_fullscreen(save=True)
        return self.analyze_image(img, prompt, file_path=path)

    def analyze_image(self, image: Image.Image, prompt: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a PIL Image using Ollama vision API."""
        b64_data = self._image_to_base64(image)
        endpoint = f"{self.ollama_url}/api/generate"

        payload = {
            "model": self.vision_model,
            "prompt": prompt,
            "images": [b64_data],
            "stream": False
        }

        try:
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "model": self.vision_model,
                    "screenshot_path": file_path
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Ollama vision connection failed: {e}. Is Ollama running with '{self.vision_model}' installed?",
                "screenshot_path": file_path
            }


visual_analyzer = VisualAnalyzer()
