"""
J.A.R.V.I.S. - Personal AI Desktop Assistant
Main Entry Point.

Usage:
    python main.py                  # Launch Mode 1: Desktop HUD Dashboard
    python main.py --mode background # Launch Mode 2: Background Voice Assistant
    python main.py --check          # Run full system diagnostics
"""

import argparse
import sys
import time
from core.brain import brain
from core.telemetry import telemetry
from voice.speaker import speaker


def print_banner():
    banner = r"""
   ╦ ╔═╗ ╦═╗ ╦  ╦ ╦ ╔═╗
   ║ ╠═╣ ╠╦╝ ╚╗╔╝ ║ ╚═╗
  ╚╝ ╩ ╩ ╩╚═  ╚╝  ╩ ╚═╝
   Desktop Tactical AI Core // Version 1.0.0
   Local GPU Acceleration Engine (RTX 3050)
    """
    print(banner)


def run_diagnostics():
    print_banner()
    print("[DIAGNOSTICS] Initializing hardware and local AI subsystems...")
    time.sleep(0.5)

    # 1. Telemetry
    stats = telemetry.get_full_telemetry()
    gpu = stats["gpu"]
    cpu = stats["cpu"]
    ram = stats["ram"]
    battery = stats["battery"]

    print(f" [+] GPU: {gpu['name']} | VRAM: {gpu['vram_used_mb']}/{gpu['vram_total_mb']} MB ({gpu['vram_percent']}%) | Temp: {gpu['temperature_c']}C")
    print(f" [+] CPU: AMD Ryzen ({cpu['cores']} logical cores) | Utilization: {cpu['percent']}%")
    print(f" [+] RAM: {ram['used_gb']} GB used / {ram['total_gb']} GB total ({ram['percent']}%)")
    print(f" [+] Battery: {battery['percent']}% ({'AC Power' if battery['power_plugged'] else 'Discharging'})")

    # 2. Agent Engine & AI Models
    st = brain.status
    if st["is_online"]:
        models = brain.list_models()
        print(f" [+] Agent Provider: {st['provider'].upper()} ONLINE ({st['endpoint']})")
        print(f" [+] Primary Model: {st['model']}")
        print(f" [+] Local Models Detected: {', '.join(models) if models else 'None'}")
    else:
        print(f" [!] Agent Engine: OFFLINE (Probed Ollama, Msty Studio, LM Studio)")
        print("     -> Start Ollama via 'ollama serve', launch Msty Studio, or start LM Studio.")
        print("     -> Recommended Agent Model: 'hermes3:8b' or 'llama3.2:3b'")

    # 3. Audio SAPI
    voices = speaker.get_available_voices()
    print(f" [+] Windows Speech (SAPI): READY ({len(voices)} local voice engines detected)")

    print("\n[DIAGNOSTICS] All primary host checks complete.\n")


def main():
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. Personal AI Desktop System")
    parser.add_argument("--mode", choices=["dashboard", "background", "check"], default="dashboard",
                        help="Operation mode: 'dashboard' (Mode 1: GUI HUD) or 'background' (Mode 2: Voice Daemon)")
    args = parser.parse_args()

    if args.mode == "check":
        run_diagnostics()
        sys.exit(0)

    print_banner()
    run_diagnostics()

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
