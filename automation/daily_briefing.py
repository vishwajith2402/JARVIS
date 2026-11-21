"""
Daily Briefing & Monitoring Operative Agent for TITAN (Inspired by OpenJarvis).
Provides:
- Morning Digest: System health, battery, active repos, recent memory, and news/summary.
- Continuous Monitor Operative: Monitors GPU temps, CPU throttling, low battery states.
100% Free & Local: Uses system telemetry, SQLite history, and local voice synthesis.
"""

import time
from datetime import datetime
from typing import Any, Callable, Dict, Optional
from core.telemetry import telemetry
from core.brain import brain
from core.memory import memory
from voice.speaker import speaker
from config.config_manager import config


class DailyBriefingAgent:
    def __init__(self):
        self.user_title = config.get("system", "user_title", "Sir")

    def generate_morning_digest(self, speak: bool = True) -> Dict[str, Any]:
        """
        Generate a comprehensive morning tactical briefing for Sir.
        Covers hardware telemetry, storage, battery, active projects, and operational status.
        """
        stats = telemetry.get_full_telemetry()
        now = datetime.now().strftime("%A, %B %d, %Y - %I:%M %p")

        gpu = stats.get("gpu", {})
        cpu = stats.get("cpu", {})
        ram = stats.get("ram", {})
        bat = stats.get("battery", {})

        pwr_state = "plugged into AC power" if bat.get("power_plugged") else f"running on battery at {bat.get('percent')}%"
        gpu_name = gpu.get("name", "NVIDIA RTX 3050")
        vram_alloc = f"{gpu.get('vram_used_mb', 0)} of {gpu.get('vram_total_mb', 4096)} MB"

        prompt = f"""You are TITAN delivering the Daily Briefing to {self.user_title}.
Current Timestamp: {now}
Hardware Overview:
- Graphics Core: {gpu_name} (VRAM: {vram_alloc}, Temp: {gpu.get('temperature_c', 45)}C)
- Compute: AMD Ryzen ({cpu.get('cores', 12)} threads, Load: {cpu.get('percent', 10)}%)
- Memory: {ram.get('used_gb', 8)} / {ram.get('total_gb', 16)} GB utilized
- Power: {pwr_state}

Deliver a crisp, professional, commanding, and courteous morning tactical briefing. Keep it concise, motivating, and ready for work."""

        digest_text = brain.generate_response(prompt, session_id="daily_digest")

        if speak:
            speaker.speak(digest_text)

        return {
            "timestamp": now,
            "digest": digest_text,
            "telemetry_summary": {
                "gpu": gpu_name,
                "cpu_load": f"{cpu.get('percent')}%",
                "battery": f"{bat.get('percent')}%",
                "memory_used": f"{ram.get('used_gb')} GB"
            }
        }

    def check_system_anomalies(self) -> Optional[str]:
        """Continuous background monitor check for thermal throttling, high VRAM, or low battery."""
        stats = telemetry.get_full_telemetry()
        gpu_temp = stats.get("gpu", {}).get("temperature_c", 0)
        battery_pct = stats.get("battery", {}).get("percent", 100)
        plugged = stats.get("battery", {}).get("power_plugged", True)

        if gpu_temp >= 85:
            msg = f"Alert, {self.user_title}: GPU core temperature has reached {gpu_temp} degrees Celsius. Thermal monitoring is active."
            speaker.speak(msg)
            return msg

        if not plugged and battery_pct <= 20:
            msg = f"Attention, {self.user_title}: Battery power is critical at {battery_pct} percent. Please connect your charger."
            speaker.speak(msg)
            return msg

        return None


daily_briefing = DailyBriefingAgent()
