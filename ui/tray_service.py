"""
Native Windows System Tray & Background Service for TITAN.
Allows TITAN to run persistently in the Windows notification tray with near 0% idle CPU.
Summons the HUD dashboard, Spotlight launcher, and routines from the tray icon.
100% Free & Local.
"""

import sys
import threading
from typing import Optional
from PIL import Image, ImageDraw

try:
    import pystray
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False

from automation.watchdog import watchdog
from automation.routines import routines
from voice.speaker import speaker


def create_arc_reactor_icon() -> Image.Image:
    """Procedurally creates a sleek 64x64 Iron Man arc-reactor icon."""
    size = (64, 64)
    image = Image.new("RGBA", size, (10, 14, 23, 255))
    draw = ImageDraw.Draw(image)

    # Outer cyan ring
    draw.ellipse([4, 4, 60, 60], outline=(0, 229, 255, 255), width=3)
    # Middle ring
    draw.ellipse([14, 14, 50, 50], outline=(0, 180, 216, 200), width=2)
    # Inner glowing core
    draw.ellipse([22, 22, 42, 42], fill=(0, 229, 255, 255))
    draw.ellipse([27, 27, 37, 37], fill=(255, 255, 255, 255))

    return image


class TitanSystemTray:
    def __init__(self, on_open_dashboard=None, on_open_spotlight=None):
        self.on_open_dashboard = on_open_dashboard
        self.on_open_spotlight = on_open_spotlight
        self._icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None

    def _menu_open_dashboard(self, icon, item):
        if self.on_open_dashboard:
            self.on_open_dashboard()
        else:
            from ui.hud_app import JarvisHudApp
            app = JarvisHudApp()
            app.run()

    def _menu_open_spotlight(self, icon, item):
        if self.on_open_spotlight:
            self.on_open_spotlight()
        else:
            from ui.spotlight import spotlight
            spotlight.show()

    def _menu_morning_briefing(self, icon, item):
        watchdog.speak_morning_briefing()

    def _menu_dev_session(self, icon, item):
        routines.execute_routine("dev_session")

    def _menu_quick_clean(self, icon, item):
        routines.execute_routine("quick_clean")

    def _menu_exit(self, icon, item):
        speaker.speak("TITAN systems shutting down. Goodbye, Sir.")
        watchdog.stop()
        if self._icon:
            self._icon.stop()
        sys.exit(0)

    def start_tray(self):
        """Starts the system tray icon in a dedicated background thread."""
        if not PYSTRAY_AVAILABLE:
            print("[SystemTray] pystray not installed; skipping system tray.")
            return

        icon_img = create_arc_reactor_icon()

        menu = pystray.Menu(
            pystray.MenuItem("Open Dashboard", self._menu_open_dashboard, default=True),
            pystray.MenuItem("Quick Spotlight (Alt+Space)", self._menu_open_spotlight),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Morning Briefing", self._menu_morning_briefing),
            pystray.MenuItem("Start Dev Session", self._menu_dev_session),
            pystray.MenuItem("Maintenance Clean", self._menu_quick_clean),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit TITAN", self._menu_exit)
        )

        self._icon = pystray.Icon("TITAN", icon_img, "TITAN Tactical AI", menu)

        def _run():
            self._icon.run()

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()


tray_service = TitanSystemTray()

if __name__ == "__main__":
    tray_service.start_tray()
    print("TITAN System Tray is active. Right-click the arc reactor icon in the taskbar.")
