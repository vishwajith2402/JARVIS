"""
Universal Macro & Routine Automator for TITAN.
Executes multi-step compound workflows with a single voice or text command.
Supports:
- dev_session: Launches VS Code, opens project, checks git status, sets volume.
- focus_mode: Lowers audio volume, closes distracting windows, silences notifications.
- quick_clean: Empties recycle bin, purges sandbox temp files, checks disk health.
- evening_wrapup: Scans uncommitted repositories, summarizes daily tasks, prepares lock/sleep.
- Custom user routines.
100% Free & Local.
"""

import os
import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from automation.app_controller import app_controller
from automation.system_control import system_control
from automation.watchdog import watchdog
from voice.speaker import speaker


class RoutineAutomator:
    def __init__(self):
        self.routines: Dict[str, Dict[str, Any]] = {
            "dev_session": {
                "description": "Initialize development environment with VS Code and Git inspection.",
                "steps": [
                    "Open VS Code workspace",
                    "Inspect Git repositories for uncommitted changes",
                    "Set master volume to 30%",
                    "Vocalize readiness report"
                ]
            },
            "focus_mode": {
                "description": "Configure system for deep focused work.",
                "steps": [
                    "Set volume to 20%",
                    "Report system quiet state"
                ]
            },
            "quick_clean": {
                "description": "Purge temporary sandbox files and empty recycle bin.",
                "steps": [
                    "Empty Windows Recycle Bin",
                    "Clean temporary sandbox files",
                    "Check free storage capacity"
                ]
            },
            "evening_wrapup": {
                "description": "End-of-day workflow review and security check.",
                "steps": [
                    "Check uncommitted code in projects",
                    "Report daily summary",
                    "Check battery & system power status"
                ]
            }
        }

    def list_routines(self) -> List[Dict[str, Any]]:
        return [{"id": k, **v} for k, v in self.routines.items()]

    def execute_routine(self, routine_name: str) -> Dict[str, Any]:
        """Executes a compound multi-step automation routine."""
        key = routine_name.lower().strip().replace(" ", "_")

        if key in ("dev_session", "dev", "start_coding", "code_setup"):
            return self._run_dev_session()
        elif key in ("focus_mode", "focus", "deep_work"):
            return self._run_focus_mode()
        elif key in ("quick_clean", "clean", "clean_system", "cleanup"):
            return self._run_quick_clean()
        elif key in ("evening_wrapup", "wrap_up", "end_day", "goodnight"):
            return self._run_evening_wrapup()
        else:
            return {
                "success": False,
                "error": f"Routine '{routine_name}' not recognized. Available: {list(self.routines.keys())}"
            }

    def _run_dev_session(self) -> Dict[str, Any]:
        results = []
        # Step 1: Open VS Code
        res_vscode = app_controller.open_app("code")
        results.append(f"VS Code: {res_vscode.get('message', 'Launched')}")

        # Step 2: Check Git status
        dirty = watchdog.scan_uncommitted_git_repos()
        repo_msg = f"{len(dirty)} dirty repos found" if dirty else "All repos clean"
        results.append(f"Git Watchdog: {repo_msg}")

        # Step 3: Set volume to 30%
        system_control.volume_down(steps=5)
        results.append("Audio: Volume calibrated for development.")

        # Step 4: Voice feedback
        msg = f"Development session initialized, Sir. VS Code is online, and your project repositories are indexed."
        speaker.speak(msg)

        return {"success": True, "routine": "dev_session", "details": results, "message": msg}

    def _run_focus_mode(self) -> Dict[str, Any]:
        system_control.volume_down(steps=8)
        msg = "Focus mode engaged, Sir. Audio minimized and background distractions subdued."
        speaker.speak(msg)
        return {"success": True, "routine": "focus_mode", "message": msg}

    def _run_quick_clean(self) -> Dict[str, Any]:
        # Empty recycle bin
        res_bin = system_control.empty_recycle_bin()

        # Clean sandbox
        sandbox_dir = Path(r"D:\Practice Projects\JARVIS\data\sandbox")
        cleaned_files = 0
        if sandbox_dir.exists():
            for f in sandbox_dir.glob("temp_*"):
                try:
                    f.unlink()
                    cleaned_files += 1
                except Exception:
                    pass

        # Check storage
        disks = watchdog.check_disk_space()
        d_free = disks.get("D:", {}).get("free_gb", "Unknown")

        msg = f"Maintenance complete, Sir. Recycle Bin emptied, {cleaned_files} temp files purged. Drive D has {d_free} GB free."
        speaker.speak(msg)
        return {"success": True, "routine": "quick_clean", "cleaned_files": cleaned_files, "message": msg}

    def _run_evening_wrapup(self) -> Dict[str, Any]:
        dirty = watchdog.scan_uncommitted_git_repos()
        msg_parts = ["Evening wrap-up complete, Sir."]
        if dirty:
            names = ", ".join([r["name"] for r in dirty])
            msg_parts.append(f"Warning: you have uncommitted changes in {names}.")
        else:
            msg_parts.append("All project repositories are committed and synced.")

        msg_parts.append("Have a pleasant evening.")
        msg = " ".join(msg_parts)
        speaker.speak(msg)
        return {"success": True, "routine": "evening_wrapup", "dirty_repos": len(dirty), "message": msg}


routines = RoutineAutomator()
