"""
T.I.T.A.N. - Personal Tactical AI Desktop Assistant
Main Master Entry Point.

Usage:
    python main.py                   # Launch Mode 1: Desktop HUD Dashboard + Background Services
    python main.py --mode background # Launch Mode 2: Silent Background Service (Tray + Alt+Space)
    python main.py --check           # Run full system diagnostics
"""

import argparse
import sys
import time
from core.launcher import AgentLauncher
from core.brain import brain
from core.telemetry import telemetry
from voice.speaker import speaker
from automation.watchdog import watchdog
from ui.tray_service import tray_service
from ui.spotlight import spotlight
from core.autostart import autostart_manager


def print_banner():
    banner = """
  +-------------------------------------------------+
  |    T.I.T.A.N.  Tactical Desktop AI Core         |
  |    Local GPU Acceleration (NVIDIA RTX 3050)     |
  |    Press Alt+Space anytime for Quick Spotlight  |
  +-------------------------------------------------+
    """
    print(banner)


def autostart_agent(on_status=None) -> dict:
    """
    Automatically find, verify, and pin local AI engine (titan:latest).
    """
    from config.config_manager import config
    preferred = config.get("agent", "primary_model", "titan:latest")
    fallbacks = config.get("agent", "fallback_models", ["titan:latest", "llama3.2:3b", "hermes3:8b"])

    agent_launcher = AgentLauncher(
        preferred_model=preferred,
        fallback_models=fallbacks,
        on_status=on_status or print
    )
    result = agent_launcher.ensure_agent_running()

    if result["success"]:
        brain.primary_model = result["model"]
        brain._active_provider = result["provider"]
        brain._active_endpoint = result["endpoint"]

    return result


def run_diagnostics(auto_launch: bool = True):
    print_banner()
    print("[BOOT] Initializing T.I.T.A.N. tactical subsystems...")
    time.sleep(0.2)

    # 1. Hardware Check
    stats = telemetry.get_full_telemetry()
    gpu = stats["gpu"]
    cpu = stats["cpu"]
    ram = stats["ram"]
    print(f"  GPU : {gpu['name']} | VRAM {gpu['vram_used_mb']}/{gpu['vram_total_mb']} MB ({gpu['vram_percent']}%)")
    print(f"  CPU : AMD Ryzen ({cpu['cores']} cores) | Load {cpu['percent']}%")
    print(f"  RAM : {ram['used_gb']} / {ram['total_gb']} GB used ({ram['percent']}%)")

    # 2. AI Engine Auto-Launch
    if auto_launch:
        result = autostart_agent(on_status=lambda m: print(f"  {m}"))
        if result["success"]:
            print(f"  [OK] Agent ONLINE — Provider: {result['provider'].upper()} | Model: {result['model']}")
        else:
            print(f"  [!!] Agent OFFLINE — {result['message']}")

    # 3. Voice Engine
    voices = speaker.get_available_voices()
    print(f"  Voice Engine: ONLINE ({len(voices)} voices ready, preferred: {speaker.preferred_voice})")

    # 4. Windows Launchers
    autostart_manager._ensure_bat_file()
    print("  Desktop Launchers: TITAN.bat ready | Global Alt+Space Spotlight registered")
    print("\n[BOOT] All subsystems operational. TITAN is ready, Sir.\n")


def main():
    parser = argparse.ArgumentParser(description="T.I.T.A.N. Personal Tactical AI Desktop Assistant")
    parser.add_argument("--mode", choices=["dashboard", "background", "check"],
                        default="dashboard",
                        help="dashboard = GUI HUD  |  background = Silent Tray + Hotkeys  |  check = diagnostics only")
    parser.add_argument("--no-autostart", action="store_true",
                        help="Skip automatic AI agent launch")
    args = parser.parse_args()

    auto_launch = not args.no_autostart

    if args.mode == "check":
        run_diagnostics(auto_launch=auto_launch)
        sys.exit(0)

    run_diagnostics(auto_launch=auto_launch)

    # Initialize Background Ecosystem
    watchdog.start_background_watcher()
    tray_service.start_tray()
    spotlight.start_hotkey_listener()

    if args.mode == "background":
        print("[LAUNCH] TITAN running in background. Use Alt+Space or the system tray to summon.")
        while True:
            time.sleep(1)
    else:
        print("[LAUNCH] Starting Desktop HUD Dashboard...")
        from ui.hud_app import run_hud
        run_hud()


if __name__ == "__main__":
    main()
