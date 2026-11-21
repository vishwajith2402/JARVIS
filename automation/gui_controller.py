"""
Universal GUI & Desktop Automation Controller for TITAN (A to Z Work).
Provides native Windows mouse and keyboard control without external dependencies.
Uses win32api, win32con, win32gui, and ctypes for instant, reliable desktop interaction.
100% Free & Local.
"""

import time
import ctypes
from typing import Any, Dict, List, Optional, Tuple

try:
    import win32api
    import win32con
    import win32gui
except ImportError:
    win32api = None
    win32con = None
    win32gui = None

# Keyboard Virtual Key Codes
VK_MAP = {
    "enter": 0x0D,
    "return": 0x0D,
    "esc": 0x1B,
    "escape": 0x1B,
    "tab": 0x09,
    "space": 0x20,
    "backspace": 0x08,
    "delete": 0x2E,
    "ctrl": 0x11,
    "control": 0x11,
    "alt": 0x12,
    "shift": 0x10,
    "win": 0x5B,
    "windows": 0x5B,
    "up": 0x26,
    "down": 0x28,
    "left": 0x25,
    "right": 0x27,
    "home": 0x24,
    "end": 0x23,
    "pageup": 0x21,
    "pagedown": 0x22,
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
    "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
    "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B
}


class DesktopGuiController:
    """Controls mouse, keyboard, and desktop windows natively on Windows 11."""

    def get_screen_size(self) -> Tuple[int, int]:
        """Returns (width, height) of primary desktop monitor."""
        user32 = ctypes.windll.user32
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    def get_mouse_position(self) -> Tuple[int, int]:
        """Returns current (x, y) coordinates of mouse cursor."""
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y

    def move_mouse(self, x: int, y: int) -> Dict[str, Any]:
        """Move cursor to absolute coordinates (x, y)."""
        try:
            ctypes.windll.user32.SetCursorPos(x, y)
            return {"success": True, "x": x, "y": y}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left", double: bool = False) -> Dict[str, Any]:
        """
        Click mouse button at specified (x, y) or current position.
        button: 'left', 'right', 'middle'
        """
        try:
            if x is not None and y is not None:
                self.move_mouse(x, y)
                time.sleep(0.05)

            user32 = ctypes.windll.user32
            b = button.lower()
            if b == "right":
                down, up = 0x0008, 0x0010  # MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP
            elif b == "middle":
                down, up = 0x0020, 0x0040  # MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP
            else:
                down, up = 0x0002, 0x0004  # MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP

            user32.mouse_event(down, 0, 0, 0, 0)
            time.sleep(0.02)
            user32.mouse_event(up, 0, 0, 0, 0)

            if double:
                time.sleep(0.08)
                user32.mouse_event(down, 0, 0, 0, 0)
                time.sleep(0.02)
                user32.mouse_event(up, 0, 0, 0, 0)

            cur_x, cur_y = self.get_mouse_position()
            return {"success": True, "clicked": b, "double": double, "position": (cur_x, cur_y)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def scroll(self, clicks: int = 3, direction: str = "down") -> Dict[str, Any]:
        """Scroll vertical wheel."""
        try:
            amount = -120 * clicks if direction.lower() == "down" else 120 * clicks
            ctypes.windll.user32.mouse_event(0x0800, 0, 0, amount, 0)  # MOUSEEVENTF_WHEEL
            return {"success": True, "scrolled": clicks, "direction": direction}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def type_text(self, text: str, delay: float = 0.01) -> Dict[str, Any]:
        """Types string into whatever window currently has focus."""
        try:
            user32 = ctypes.windll.user32
            for char in text:
                vk = user32.VkKeyScanW(ord(char))
                code = vk & 0xFF
                shift = (vk >> 8) & 1

                if shift:
                    user32.keybd_event(0x10, 0, 0, 0)  # Shift down

                user32.keybd_event(code, 0, 0, 0)
                time.sleep(0.005)
                user32.keybd_event(code, 0, 2, 0)  # KEYEVENTF_KEYUP

                if shift:
                    user32.keybd_event(0x10, 0, 2, 0)  # Shift up

                if delay > 0:
                    time.sleep(delay)

            return {"success": True, "typed_length": len(text)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_hotkey(self, keys: List[str]) -> Dict[str, Any]:
        """
        Press and release a combination of keys (e.g. ['ctrl', 'c'], ['win', 'r'], ['alt', 'tab']).
        """
        user32 = ctypes.windll.user32
        key_codes = []
        for k in keys:
            k_low = k.lower().strip()
            if k_low in VK_MAP:
                key_codes.append(VK_MAP[k_low])
            elif len(k_low) == 1:
                key_codes.append(user32.VkKeyScanW(ord(k_low)) & 0xFF)

        if not key_codes:
            return {"success": False, "error": f"Invalid key sequence: {keys}"}

        try:
            # Press keys down in order
            for code in key_codes:
                user32.keybd_event(code, 0, 0, 0)
                time.sleep(0.01)

            time.sleep(0.03)

            # Release keys in reverse order
            for code in reversed(key_codes):
                user32.keybd_event(code, 0, 2, 0)
                time.sleep(0.01)

            return {"success": True, "hotkey": "+".join(keys)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def minimize_active_window(self) -> Dict[str, Any]:
        """Minimize foreground window."""
        try:
            if win32gui and win32con:
                hwnd = win32gui.GetForegroundWindow()
                if hwnd:
                    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                    return {"success": True, "message": "Foreground window minimized."}
            return {"success": False, "message": "No window focused."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def maximize_active_window(self) -> Dict[str, Any]:
        """Maximize foreground window."""
        try:
            if win32gui and win32con:
                hwnd = win32gui.GetForegroundWindow()
                if hwnd:
                    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                    return {"success": True, "message": "Foreground window maximized."}
            return {"success": False, "message": "No window focused."}
        except Exception as e:
            return {"success": False, "error": str(e)}


gui_controller = DesktopGuiController()
