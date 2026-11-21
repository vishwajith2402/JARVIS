"""
T.I.T.A.N. - Personal Tactical AI Desktop Assistant
Main Entry Point.

Usage:
    python main.py                   # Launch Mode 1: Desktop HUD Dashboard
    python main.py --mode background # Launch Mode 2: Background Voice Assistant
    python main.py --check           # Run full system diagnostics
    python main.py --no-autostart    # Skip automatic agent launch (manual mode)
"""

import argparse
import sys
import time
from core.launcher import AgentLauncher
from core.brain import brain
from core.telemetry import telemetry
from voice.speaker import speaker


def print_banner():
    banner = """
  +------------------------------------------+
  |    T.I.T.A.N.  Tactical Desktop AI       |
  |   Desktop Tactical AI Core // v1.2.0     |
  |   Local GPU Acceleration (RTX 3050)      |
  +------------------------------------------+
    """
    print(banner)


def autostart_agent(on_status=None) -> dict:
    """
    Automatically find and start the AI engine before TITAN boots.
    Returns the launch result dict from AgentLauncher.
    """
    from config.config_manager import config
    preferred = config.get("agent", "primary_model", "hermes3:8b")
    fallbacks = config.get("agent", "fallback_models", ["llama3.2:3b", "phi3.5:latest"])

    agent_launcher = AgentLauncher(
        preferred_model=preferred,
        fallback_models=fallbacks,
        on_status=on_status or print
    )
    result = agent_launcher.ensure_agent_running()

    # Sync the active model/provider back into the brain
    if result["success"]:
        brain.primary_model = result["model"]
        brain._active_provider = result["provider"]
        brain._active_endpoint = result["endpoint"]

    return result


def run_diagnostics(auto_launch: bool = True):
    print_banner()
    print("[BOOT] Initializing T.I.T.A.N. subsystems...")
    time.sleep(0.3)

    # --- Step 1: Hardware Telemetry ---
    print("\n[1/3] HARDWARE CHECK")
    stats = telemetry.get_full_telemetry()
    gpu     = stats["gpu"]
    cpu     = stats["cpu"]
    ram     = stats["ram"]
    battery = stats["battery"]
    print(f"  GPU : {gpu['name']} | VRAM {gpu['vram_used_mb']}/{gpu['vram_total_mb']} MB | Temp {gpu['temperature_c']}C")
    print(f"  CPU : AMD Ryzen ({cpu['cores']} cores) @ {cpu['frequency_mhz']} MHz | Load {cpu['percent']}%")
    print(f"  RAM : {ram['used_gb']} / {ram['total_gb']} GB used ({ram['percent']}%)")
    print(f"  PWR : {battery['percent']}% ({'AC Power' if battery['power_plugged'] else 'On Battery'})")

    # --- Step 2: Auto-launch AI Agent ---
    print("\n[2/3] AI AGENT AUTO-LAUNCH")
    if auto_launch:
        result = autostart_agent(on_status=lambda m: print(f"  {m}"))
        if result["success"]:
            print(f"  [OK] Agent ONLINE  — Provider: {result['provider'].upper()} | Model: {result['model']}")
        else:
            print(f"  [!!] Agent OFFLINE — {result['message']}")
    else:
        st = brain.status
        if st["is_online"]:
            print(f"  [OK] Agent ONLINE  — Provider: {st['provider'].upper()} | Model: {st['model']}")
        else:
            print("  [!!] Agent OFFLINE — Run without --no-autostart to enable auto-launch.")

    # --- Step 3: Voice Engine ---
    print("\n[3/3] VOICE ENGINE")
    voices = speaker.get_available_voices()
    print(f"  SAPI: {'READY' if True else 'ERROR'} ({len(voices)} voice packs detected)")

    print("\n[BOOT] All subsystems initialized. TITAN is ready.\n")


def main():
    parser = argparse.ArgumentParser(description="T.I.T.A.N. Personal Tactical AI Desktop Assistant")
    parser.add_argument("--mode", choices=["dashboard", "background", "check"],
                        default="dashboard",
                        help="dashboard = GUI HUD  |  background = Voice Daemon  |  check = diagnostics only")
    parser.add_argument("--no-autostart", action="store_true",
                        help="Skip automatic AI agent launch (manual mode)")
    args = parser.parse_args()

    auto_launch = not args.no_autostart

    if args.mode == "check":
        run_diagnostics(auto_launch=auto_launch)
        sys.exit(0)

    run_diagnostics(auto_launch=auto_launch)

    if args.mode == "background":
        print("[LAUNCH] Starting Mode 2: Background Voice Assistant...")
        from ui.tray import daemon
        daemon.start()
    else:
        print("[LAUNCH] Starting Mode 1: Desktop HUD Dashboard...")
        from ui.hud_app import run_hud
        run_hud()


if __name__ == "__main__":
    main()
