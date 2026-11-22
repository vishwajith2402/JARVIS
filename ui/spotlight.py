"""
TITAN Global Spotlight Quick Launcher.
Summonable from anywhere on Windows using Alt+Space.
Provides instant multi-tasking without switching away from your current software.
100% Free & Local.
"""

import sys
import time
import ctypes
import threading
from pathlib import Path
from typing import Optional
import webview

from core.brain import brain
from voice.speaker import speaker
from voice.listener import listener
from automation.app_controller import app_controller
from automation.system_control import system_control

SPOTLIGHT_HTML = Path(__file__).resolve().parent / "static" / "spotlight.html"


class SpotlightApiBridge:
    def __init__(self, manager):
        self.manager = manager

    def hide_spotlight(self) -> None:
        self.manager.hide()

    def listen_voice(self) -> str:
        text = listener.listen_once()
        return text or ""

    def execute_command(self, query: str) -> str:
        if not query or not query.strip():
            return ""

        query_lower = query.lower().strip()

        # Instant local handlers for lightning response
        if query_lower in ("mute", "unmute"):
            system_control.volume_mute()
            return "Volume mute toggled, Sir."
        elif "volume up" in query_lower:
            system_control.volume_up(5)
            return "Volume increased by 10%."
        elif "volume down" in query_lower:
            system_control.volume_down(5)
            return "Volume decreased by 10%."
        elif query_lower.startswith("open "):
            target = query[5:].strip()
            res = app_controller.open_app(target)
            return res.get("message", f"Opened {target}, Sir.")
        elif query_lower.startswith("close "):
            target = query[6:].strip()
            res = app_controller.close_app(target)
            return res.get("message", f"Closed {target}, Sir.")

        # Full AI Agent fallback
        reply = brain.chat(query)
        speaker.speak(reply)
        return reply


class SpotlightManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpotlightManager, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self._window: Optional[webview.Window] = None
        self._is_visible = False
        self._bridge = SpotlightApiBridge(self)
        self._hotkey_thread = None

    def start_hotkey_listener(self, on_trigger=None):
        """Starts background Win32 message pump for Alt+Space global hotkey."""
        def _loop():
            user32 = ctypes.windll.user32
            HOTKEY_ID = 101
            MOD_ALT = 0x0001
            MOD_NOREPEAT = 0x4000
            VK_SPACE = 0x20

            # Register Alt + Space
            if not user32.RegisterHotKey(None, HOTKEY_ID, MOD_ALT | MOD_NOREPEAT, VK_SPACE):
                # Fallback: try Ctrl + Space if Alt + Space is claimed
                MOD_CONTROL = 0x0002
                user32.RegisterHotKey(None, HOTKEY_ID, MOD_CONTROL | MOD_NOREPEAT, VK_SPACE)

            msg = ctypes.wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == 0x0312:  # WM_HOTKEY
                    if on_trigger:
                        on_trigger()
                    else:
                        self.toggle()
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))

        self._hotkey_thread = threading.Thread(target=_loop, daemon=True)
        self._hotkey_thread.start()

    def show(self):
        if self._window:
            self._window.show()
            self._window.restore()
            self._is_visible = True

    def hide(self):
        if self._window:
            self._window.hide()
            self._is_visible = False

    def toggle(self):
        if self._is_visible:
            self.hide()
        else:
            self.show()

    def launch(self):
        """Launches the dedicated Spotlight webview window."""
        self._window = webview.create_window(
            title="TITAN Spotlight",
            url=str(SPOTLIGHT_HTML),
            width=680,
            height=340,
            resizable=False,
            frameless=True,
            easy_drag=True,
            on_top=True,
            js_api=self._bridge,
            background_color="#00000000"
        )
        self._is_visible = True
        self.start_hotkey_listener()
        webview.start()


spotlight = SpotlightManager()

if __name__ == "__main__":
    spotlight.launch()
