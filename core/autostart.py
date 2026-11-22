"""
Windows Auto-Start & Desktop Launcher Manager for TITAN.
Features:
1. Double-clickable desktop shortcut and launcher (.bat / .lnk).
2. Windows Startup Registry toggle (auto-boot on PC startup).
100% Free & Local.
"""

import os
import sys
import winreg
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYTHON_EXE = sys.executable
MAIN_PY = PROJECT_ROOT / "main.py"
REG_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "TITAN_AI_Assistant"


class AutoStartManager:
    def __init__(self):
        self.bat_path = PROJECT_ROOT / "TITAN.bat"
        self._ensure_bat_file()

    def _ensure_bat_file(self) -> Path:
        """Create the double-clickable Windows batch launcher."""
        bat_content = f"""@echo off
title TITAN Desktop AI
cd /d "{PROJECT_ROOT}"
start "" "{PYTHON_EXE}" "{MAIN_PY}"
exit
"""
        with open(self.bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
        return self.bat_path

    def create_desktop_shortcut(self) -> Dict[str, Any]:
        """Creates a Windows shortcut on the user's desktop."""
        try:
            import win32com.client
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "TITAN.lnk"

            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.TargetPath = str(self.bat_path)
            shortcut.WorkingDirectory = str(PROJECT_ROOT)
            shortcut.Description = "TITAN Tactical AI Personal Assistant"
            shortcut.save()

            return {
                "success": True,
                "shortcut_path": str(shortcut_path),
                "message": f"Desktop shortcut created at: {shortcut_path}"
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to create desktop shortcut: {e}"}

    def set_autostart(self, enable: bool = True) -> Dict[str, Any]:
        """Enable or disable silent startup on Windows boot."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY_PATH, 0, winreg.KEY_ALL_ACCESS)
            if enable:
                cmd = f'"{PYTHON_EXE}" "{MAIN_PY}" --mode background'
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
                msg = "TITAN set to start automatically with Windows, Sir."
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                    msg = "TITAN auto-start on Windows boot disabled."
                except FileNotFoundError:
                    msg = "TITAN was not set to auto-start."
            winreg.CloseKey(key)
            return {"success": True, "enabled": enable, "message": msg}
        except Exception as e:
            return {"success": False, "error": f"Registry modification error: {e}"}

    def is_autostart_enabled(self) -> bool:
        """Check if TITAN is configured to start on boot."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_KEY_PATH, 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return bool(val)
        except Exception:
            return False


autostart_manager = AutoStartManager()

if __name__ == "__main__":
    res = autostart_manager.create_desktop_shortcut()
    print(res)
