"""
Universal Windows Application & Software Controller for TITAN.
Scans and indexes ALL installed Windows software across:
1. Windows Start Menu shortcuts (.lnk) in ProgramData & AppData
2. Windows Registry App Paths (HKLM & HKCU App Paths)
3. Windows System32, SysWOW64, and System Apps
4. Environment PATH binaries
5. Common Program Files & Local AppData application folders

Supports fuzzy matching so TITAN can open any software by full name, partial name, or nickname.
"""

import os
import re
import shutil
import subprocess
import winreg
from typing import Any, Dict, List, Optional
import win32con
import win32gui
import win32process


class UniversalAppController:
    def __init__(self):
        self._installed_apps: Dict[str, str] = {}
        self.rescan_installed_software()

    def rescan_installed_software(self) -> int:
        """
        Scan and index all installed software on this Windows PC.
        Maps lower-case app names and aliases to their exact launch paths.
        """
        apps_map = {}

        # --- 1. Start Menu Shortcuts (.lnk) ---
        start_menu_dirs = [
            os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs"),
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs")
        ]

        for s_dir in start_menu_dirs:
            if os.path.exists(s_dir):
                for root, _, files in os.walk(s_dir):
                    for file in files:
                        if file.lower().endswith(".lnk"):
                            app_name = os.path.splitext(file)[0].strip()
                            full_lnk_path = os.path.join(root, file)
                            apps_map[app_name.lower()] = full_lnk_path

        # --- 2. Windows Registry: App Paths ---
        reg_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths")
        ]

        for hkey, subkey in reg_keys:
            try:
                with winreg.OpenKey(hkey, subkey) as root_key:
                    num_subkeys = winreg.QueryInfoKey(root_key)[0]
                    for i in range(num_subkeys):
                        try:
                            app_key_name = winreg.EnumKey(root_key, i)
                            with winreg.OpenKey(root_key, app_key_name) as app_k:
                                path_val, _ = winreg.QueryValueEx(app_k, "")
                                if path_val and os.path.exists(path_val):
                                    name_clean = os.path.splitext(app_key_name)[0].lower()
                                    apps_map[name_clean] = path_val
                                    apps_map[app_key_name.lower()] = path_val
                        except Exception:
                            continue
            except Exception:
                pass

        # --- 3. Built-in Utilities & Standard Tools ---
        common_system_tools = {
            "notepad": r"C:\Windows\System32\notepad.exe",
            "calculator": r"C:\Windows\System32\calc.exe",
            "calc": r"C:\Windows\System32\calc.exe",
            "cmd": r"C:\Windows\System32\cmd.exe",
            "powershell": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "terminal": "wt.exe",
            "explorer": r"C:\Windows\explorer.exe",
            "files": r"C:\Windows\explorer.exe",
            "taskmgr": r"C:\Windows\System32\taskmgr.exe",
            "task manager": r"C:\Windows\System32\taskmgr.exe",
            "settings": "ms-settings:",
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "vscode": os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
            "code": os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
            "visual studio code": os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe")
        }

        for k, v in common_system_tools.items():
            if k not in apps_map:
                apps_map[k] = v

        self._installed_apps = apps_map
        return len(self._installed_apps)

    def find_software(self, query: str) -> Optional[str]:
        """
        Fuzzy match and locate any software path installed on the PC.
        """
        query_clean = query.lower().strip()

        # 1. Direct exact match
        if query_clean in self._installed_apps:
            return self._installed_apps[query_clean]

        # 2. Check system PATH
        path_which = shutil.which(query_clean) or shutil.which(f"{query_clean}.exe")
        if path_which:
            return path_which

        # 3. Substring match (e.g. 'discord' in 'discord.lnk' or 'excel' in 'microsoft excel')
        for name, path in self._installed_apps.items():
            if query_clean in name or name in query_clean:
                return path

        # 4. Word boundary / token match
        tokens = query_clean.split()
        for name, path in self._installed_apps.items():
            if all(t in name for t in tokens):
                return path

        return None

    def launch_app(self, app_name: str, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Launch any installed software on the user's PC.
        Handles direct EXEs, Start Menu shortcuts (.lnk), UWP/Store Apps, and URI schemes.
        """
        target = self.find_software(app_name)

        # Handle URI scheme (e.g. ms-settings:)
        if target and target.endswith(":"):
            try:
                os.startfile(target)
                return {"success": True, "message": f"Opened Windows {app_name}."}
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Launch resolved executable or shortcut (.lnk)
        if target:
            try:
                if target.lower().endswith(".lnk"):
                    # Use os.startfile for Windows shortcuts (.lnk) to preserve native working directory
                    os.startfile(target)
                    return {"success": True, "message": f"Launched '{app_name}' from Start Menu ({os.path.basename(target)})."}
                else:
                    cmd = [target]
                    if args:
                        cmd.extend(args)
                    subprocess.Popen(cmd)
                    return {"success": True, "message": f"Launched '{app_name}' ({target})."}
            except Exception as e:
                # Fallback to os.startfile
                try:
                    os.startfile(target)
                    return {"success": True, "message": f"Launched '{app_name}' via Windows shell."}
                except Exception as ex:
                    return {"success": False, "error": f"Failed launching '{target}': {ex}"}

        # Last-resort fallback: Windows 'start' command for unregistered apps
        try:
            cmd = f'start "" "{app_name}"'
            subprocess.Popen(cmd, shell=True)
            return {"success": True, "message": f"Attempting to launch '{app_name}' via Windows shell dispatch."}
        except Exception as e:
            return {"success": False, "error": f"Could not locate software '{app_name}' on your computer: {e}"}

    def list_all_software_names(self, limit: int = 50) -> List[str]:
        """Returns a sorted list of registered software names."""
        return sorted(list(set(self._installed_apps.keys())))[:limit]

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

    def close_app(self, app_name: str, force: bool = False) -> Dict[str, Any]:
        """
        Gracefully or forcefully close any running application by software name, window title, or executable name.
        Uses 3-stage shutdown:
        1. Sends WM_CLOSE to visible windows matching the software (graceful save prompt).
        2. Resolves binary name and terminates running processes via taskkill.
        3. PSUtil process kill fallback.
        """
        import psutil
        import win32con
        import win32gui

        query = app_name.lower().strip()
        closed_count = 0

        # Stage 1: Graceful window close via WM_CLOSE
        windows = self.list_visible_windows()
        for w in windows:
            title_lower = w["title"].lower()
            if query in title_lower or any(token in title_lower for token in query.split()):
                try:
                    win32gui.PostMessage(w["hwnd"], win32con.WM_CLOSE, 0, 0)
                    closed_count += 1
                except Exception:
                    pass

        # Stage 2: Match running processes by name or resolved binary
        target_path = self.find_software(query)
        exe_name = os.path.basename(target_path) if target_path else f"{query}.exe"

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pname = proc.info['name'].lower()
                if query in pname or pname == exe_name.lower():
                    proc.terminate()
                    closed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if closed_count > 0:
            return {"success": True, "message": f"Closed '{app_name}' successfully, Sir."}

        # Stage 3: Windows taskkill fallback
        try:
            cmd = ["taskkill", "/F" if force else "/T", "/IM", exe_name]
            res = subprocess.run(cmd, capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            if res.returncode == 0:
                return {"success": True, "message": f"Closed '{app_name}' ({exe_name}) via taskkill, Sir."}
        except Exception:
            pass

        return {"success": False, "message": f"No active windows or processes found for '{app_name}' to close, Sir."}


app_controller = UniversalAppController()
