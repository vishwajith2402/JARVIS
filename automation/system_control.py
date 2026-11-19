"""
System Controls for JARVIS.
Handles volume control, screen lock, power queries, and desktop notifications.
"""

import ctypes
import subprocess
from typing import Any, Dict


class SystemControl:
    def lock_workstation(self) -> Dict[str, Any]:
        """Locks the Windows workstation securely."""
        try:
            ctypes.windll.user32.LockWorkStation()
            return {"success": True, "message": "Workstation locked successfully."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def volume_mute(self) -> Dict[str, Any]:
        """Toggle mute on master audio volume."""
        VK_VOLUME_MUTE = 0xAD
        ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
        ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 2, 0)
        return {"success": True, "message": "Volume mute toggled."}

    def volume_up(self, steps: int = 5) -> Dict[str, Any]:
        VK_VOLUME_UP = 0xAF
        for _ in range(steps):
            ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 2, 0)
        return {"success": True, "message": f"Volume raised by {steps * 2}%."}

    def volume_down(self, steps: int = 5) -> Dict[str, Any]:
        VK_VOLUME_DOWN = 0xAE
        for _ in range(steps):
            ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
            ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 2, 0)
        return {"success": True, "message": f"Volume lowered by {steps * 2}%."}


system_control = SystemControl()
