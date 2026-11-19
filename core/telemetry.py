"""
Hardware Telemetry for JARVIS.
Monitors CPU, RTX 3050 GPU, RAM, Battery, and Disk.
"""

import shutil
import subprocess
from typing import Any, Dict, Optional
import psutil


class TelemetryMonitor:
    def __init__(self):
        self._last_stats = {}

    def get_gpu_stats(self) -> Dict[str, Any]:
        """Query NVIDIA RTX 3050 via nvidia-smi command with fast execution."""
        gpu_info = {
            "name": "NVIDIA GeForce RTX 3050",
            "vram_used_mb": 0,
            "vram_total_mb": 4096,
            "vram_percent": 0.0,
            "gpu_util_percent": 0,
            "temperature_c": 0,
            "available": False
        }
        try:
            cmd = [
                "nvidia-smi",
                "--query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu",
                "--format=csv,noheader,nounits"
            ]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=2,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
            if result.returncode == 0 and result.stdout.strip():
                parts = [p.strip() for p in result.stdout.strip().split(",")]
                if len(parts) >= 5:
                    gpu_info["name"] = parts[0]
                    vram_used = float(parts[1])
                    vram_total = float(parts[2])
                    gpu_info["vram_used_mb"] = int(vram_used)
                    gpu_info["vram_total_mb"] = int(vram_total)
                    gpu_info["vram_percent"] = round((vram_used / vram_total) * 100, 1) if vram_total > 0 else 0
                    gpu_info["gpu_util_percent"] = int(parts[3])
                    gpu_info["temperature_c"] = int(parts[4])
                    gpu_info["available"] = True
        except Exception:
            gpu_info["available"] = False

        return gpu_info

    def get_cpu_stats(self) -> Dict[str, Any]:
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_count = psutil.cpu_count(logical=True)
        freq = psutil.cpu_freq()
        current_mhz = int(freq.current) if freq else 0
        return {
            "percent": cpu_percent,
            "cores": cpu_count,
            "frequency_mhz": current_mhz
        }

    def get_ram_stats(self) -> Dict[str, Any]:
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024 ** 3), 2),
            "used_gb": round(mem.used / (1024 ** 3), 2),
            "available_gb": round(mem.available / (1024 ** 3), 2),
            "percent": mem.percent
        }

    def get_battery_stats(self) -> Dict[str, Any]:
        battery = psutil.sensors_battery()
        if battery is None:
            return {"percent": 100, "power_plugged": True, "time_left_min": -1}
        return {
            "percent": battery.percent,
            "power_plugged": battery.power_plugged,
            "time_left_min": int(battery.secsleft / 60) if battery.secsleft > 0 else -1
        }

    def get_disk_stats(self) -> Dict[str, Any]:
        disks = {}
        for path in ["C:\\", "D:\\"]:
            try:
                usage = shutil.disk_usage(path)
                disks[path[0]] = {
                    "total_gb": round(usage.total / (1024 ** 3), 1),
                    "free_gb": round(usage.free / (1024 ** 3), 1),
                    "percent_used": round(((usage.total - usage.free) / usage.total) * 100, 1)
                }
            except Exception:
                pass
        return disks

    def get_full_telemetry(self) -> Dict[str, Any]:
        stats = {
            "gpu": self.get_gpu_stats(),
            "cpu": self.get_cpu_stats(),
            "ram": self.get_ram_stats(),
            "battery": self.get_battery_stats(),
            "disk": self.get_disk_stats()
        }
        self._last_stats = stats
        return stats


telemetry = TelemetryMonitor()
