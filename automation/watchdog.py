"""
Proactive Autonomous Watchdog & Morning Briefing Engine for TITAN.
Monitors:
1. Hardware health (RTX 3050 VRAM, Ryzen 5 load, disk space, battery).
2. Uncommitted Git repositories across local development directories.
3. Proactive Morning Briefing with scheduling and voice synthesis.
100% Free & Local.
"""

import os
import shutil
import datetime
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.telemetry import telemetry
from voice.speaker import speaker


class AutonomousWatchdog:
    def __init__(self, check_interval_minutes: int = 15):
        self.interval = check_interval_minutes * 60
        self.dev_roots = [
            Path(r"D:\Practice Projects"),
            Path(r"D:\Extra"),
        ]
        self._running = False
        self._watcher_thread: Optional[threading.Thread] = None

    def start_background_watcher(self) -> None:
        """Starts low-impact background guardian thread."""
        if self._running:
            return
        self._running = True

        def _loop():
            while self._running:
                try:
                    self.perform_health_check()
                except Exception as e:
                    print(f"[Watchdog] Error in guardian cycle: {e}")
                time.sleep(self.interval)

        self._watcher_thread = threading.Thread(target=_loop, daemon=True)
        self._watcher_thread.start()

    def stop(self) -> None:
        self._running = False

    def check_disk_space(self) -> Dict[str, Dict[str, float]]:
        """Check free storage space on Windows drives."""
        drives = {}
        for drive in ("C:", "D:"):
            try:
                usage = shutil.disk_usage(drive)
                drives[drive] = {
                    "total_gb": round(usage.total / (1024 ** 3), 1),
                    "used_gb": round(usage.used / (1024 ** 3), 1),
                    "free_gb": round(usage.free / (1024 ** 3), 1),
                    "percent_free": round((usage.free / usage.total) * 100, 1)
                }
            except Exception:
                pass
        return drives

    def scan_uncommitted_git_repos(self) -> List[Dict[str, Any]]:
        """Scans developer directories for dirty git trees and uncommitted code."""
        dirty_repos = []
        for root in self.dev_roots:
            if not root.exists():
                continue
            for item in root.iterdir():
                if item.is_dir() and (item / ".git").exists():
                    try:
                        res = subprocess.run(
                            ["git", "-C", str(item), "status", "--porcelain"],
                            capture_output=True,
                            text=True,
                            timeout=3
                        )
                        if res.returncode == 0:
                            lines = [l for l in res.stdout.strip().split("\n") if l.strip()]
                            if lines:
                                dirty_repos.append({
                                    "name": item.name,
                                    "path": str(item),
                                    "uncommitted_files_count": len(lines),
                                    "files": [l.strip()[:40] for l in lines[:3]]
                                })
                    except Exception:
                        continue
        return dirty_repos

    def perform_health_check(self) -> Dict[str, Any]:
        """Comprehensive system diagnostics check."""
        tel = telemetry.get_full_telemetry()
        disks = self.check_disk_space()
        dirty_repos = self.scan_uncommitted_git_repos()

        alerts = []
        # VRAM alert
        vram_pct = tel["gpu"]["vram_percent"]
        if vram_pct > 88:
            alerts.append(f"VRAM usage is high: {vram_pct}% ({tel['gpu']['vram_used_mb']}/{tel['gpu']['vram_total_mb']} MB)")

        # Disk alert
        for d, stats in disks.items():
            if stats["free_gb"] < 10.0:
                alerts.append(f"Drive {d} has only {stats['free_gb']} GB remaining.")

        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "telemetry": tel,
            "disks": disks,
            "dirty_repos": dirty_repos,
            "alerts": alerts
        }

    def generate_morning_briefing(self) -> str:
        """
        Creates a professional, personalized tactical morning briefing.
        """
        now = datetime.datetime.now()
        hour = now.hour
        greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 18 else "Good evening")
        date_str = now.strftime("%A, %B %d, %Y")
        time_str = now.strftime("%I:%M %p")

        diag = self.perform_health_check()
        tel = diag["telemetry"]
        gpu = tel["gpu"]
        cpu = tel["cpu"]
        ram = tel["ram"]
        battery = tel["battery"]
        dirty_repos = diag["dirty_repos"]

        briefing_lines = [
            f"{greeting}, Sir. The time is {time_str} on {date_str}.",
            f"All workstation diagnostics are online.",
            f"Hardware Status: GPU {gpu['name']} is operating at {gpu['vram_used_mb']} MB VRAM utilization ({gpu['vram_percent']}%). CPU load is {cpu['percent']}%, and system RAM is {ram['percent']}%."
        ]

        if battery.get("percent") is not None:
            plugged = "connected to AC power" if battery.get("plugged") else "on battery power"
            briefing_lines.append(f"Battery is at {battery['percent']}% ({plugged}).")

        if dirty_repos:
            repo_names = ", ".join([r["name"] for r in dirty_repos[:3]])
            briefing_lines.append(f"Workspace Watchdog: You have {len(dirty_repos)} repositories with uncommitted changes ({repo_names}).")
        else:
            briefing_lines.append("Workspace Watchdog: All local repositories are cleanly committed.")

        briefing_lines.append("TITAN is ready at your command. How may I assist you today, Sir?")

        full_text = " ".join(briefing_lines)
        return full_text

    def speak_morning_briefing(self) -> str:
        briefing = self.generate_morning_briefing()
        speaker.speak(briefing)
        return briefing


watchdog = AutonomousWatchdog()
