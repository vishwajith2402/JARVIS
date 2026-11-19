"""
Windows Application Controller for JARVIS.
Handles application discovery, launching, window focus, and process tracking.
"""

import os
import shutil
import subprocess
from typing import Any, Dict, List, Optional
import win32gui
import win32con
import win32process


class AppController:
    KNOWN_APPS = {
        "vscode": ["code.cmd", "code.exe", "Code.exe"],
        "code": ["code.cmd", "code.exe", "Code.exe"],
        "chrome": ["chrome.exe"],
        "browser": ["chrome.exe", "msedge.exe"],
        "edge": ["msedge.exe"],
        "notepad": ["notepad.exe"],
        "calculator": ["calc.exe"],
        "terminal": ["wt.exe", "powershell.exe", "cmd.exe"],
        "explorer": ["explorer.exe"]
    }

    def _resolve_executable(self, app_name: str) -> Optional[str]:
        app_lower = app_name.lower().strip()
        candidates = self.KNOWN_APPS.get(app_lower, [app_name, f"{app_name}.exe"])

        for candidate in candidates:
            resolved = shutil.which(candidate)
            if resolved:
                return resolved

        # Common Windows paths
        common_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Microsoft\Edge\Application\msedge.exe"),
            r"C:\Windows\System32\notepad.exe",
            r"C:\Windows\System32\calc.exe",
            r"C:\Windows\explorer.exe"
        ]
        for p in common_paths:
            if os.path.exists(p) and app_lower in p.lower():
                return p

        return None

    def launch_app(self, app_name: str, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Launch an application with optional arguments (such as a project directory for VS Code)."""
        exe_path = self._resolve_executable(app_name)
        if not exe_path:
            # Fallback to direct Windows start command
            try:
                cmd = ["cmd", "/c", "start", app_name]
                if args:
                    cmd.extend(args)
                subprocess.Popen(cmd, shell=True)
                return {"success": True, "message": f"Initiated launch for '{app_name}' via Windows shell."}
            except Exception as e:
                return {"success": False, "error": f"Application '{app_name}' could not be located: {e}"}

        try:
            full_cmd = [exe_path]
            if args:
                full_cmd.extend(args)
            subprocess.Popen(full_cmd)
            return {"success": True, "message": f"Successfully launched '{app_name}' ({exe_path})."}
        except Exception as e:
            return {"success": False, "error": f"Failed to execute '{exe_path}': {e}"}

    def list_visible_windows(self) -> List[Dict[str, Any]]:
        """List all top-level visible Windows with titles."""
        windows = []

        def enum_handler(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title.strip():
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    windows.append({"hwnd": hwnd, "title": title, "pid": pid})

        win32gui.EnumWindows(enum_handler, None)
        return windows

    def focus_window_by_title(self, query: str) -> bool:
        """Find a window matching the query string and bring it to foreground."""
        query_lower = query.lower()
        windows = self.list_visible_windows()
        for w in windows:
            if query_lower in w["title"].lower():
                try:
                    hwnd = w["hwnd"]
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    return True
                except Exception:
                    pass
        return False


app_controller = AppController()
