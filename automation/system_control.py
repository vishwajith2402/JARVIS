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

    def set_brightness(self, level_pct: int) -> Dict[str, Any]:
        """Adjust laptop monitor brightness (0-100%)."""
        val = max(0, min(100, int(level_pct)))
        ps_cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{val})"
        try:
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                return {"success": True, "message": f"Display brightness set to {val}%."}
            return {"success": False, "error": res.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def sleep_system(self) -> Dict[str, Any]:
        """Puts Windows workstation to sleep."""
        try:
            ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)
            return {"success": True, "message": "System transitioning to sleep."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def empty_recycle_bin(self) -> Dict[str, Any]:
        """Silently empties the Windows Recycle Bin."""
        try:
            # SHERB_NOCONFIRMATION = 0x00000001, SHERB_NOPROGRESSUI = 0x00000002, SHERB_NOSOUND = 0x00000004
            flags = 0x00000001 | 0x00000002 | 0x00000004
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, flags)
            return {"success": True, "message": "Recycle Bin emptied successfully."}
        except Exception as e:
            return {"success": False, "error": str(e)}


system_control = SystemControl()
