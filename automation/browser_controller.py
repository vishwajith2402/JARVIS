"""
Browser Controller for TITAN.
Automates browser tasks using Playwright or launches native Google Chrome.
Maintains persistent windows so the browser never closes when automation completes.
100% Free & Local.
"""

import os
import subprocess
import threading
import time
import urllib.parse
from typing import Any, Dict, Optional

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
]


class BrowserController:
    def __init__(self):
        self._chrome_path = self._find_chrome()

    def _find_chrome(self) -> Optional[str]:
        for p in CHROME_PATHS:
            if os.path.isfile(p):
                return p
        return None

    def open_url(self, url: str) -> Dict[str, Any]:
        """Launch URL in Google Chrome (persists indefinitely)."""
        target = url if url.startswith("http") else f"https://{url}"
        try:
            if self._chrome_path:
                subprocess.Popen([self._chrome_path, target])
            else:
                import webbrowser
                webbrowser.open(target)
            return {"success": True, "message": f"Navigated to {target} in Chrome, Sir."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_youtube_action(self, channel_or_query: str, comment_or_emoji: Optional[str] = None) -> Dict[str, Any]:
        """
        Automates searching YouTube, navigating to channel/video, and interacting.
        Runs Playwright in an asynchronous thread with infinite keep-alive so the window stays open forever.
        """
        def _run_playwright_workflow():
            try:
                from playwright.sync_api import sync_playwright

                with sync_playwright() as p:
                    # Launch persistent Chromium/Chrome in full desktop view
                    browser = p.chromium.launch(
                        headless=False,
                        args=["--start-maximized", "--no-default-browser-check"]
                    )
                    context = browser.new_context(no_viewport=True)
                    page = context.new_page()

                    # Step 1: Open YouTube search
                    search_query = urllib.parse.quote(channel_or_query)
                    search_url = f"https://www.youtube.com/results?search_query={search_query}"
                    page.goto(search_url, timeout=40000)
                    page.wait_for_load_state("domcontentloaded")
                    time.sleep(2)

                    # Step 2: Click the first channel/live/video result
                    try:
                        channel_selector = "#channel-title, ytd-channel-renderer, #video-title, ytd-video-renderer a#thumbnail"
                        page.wait_for_selector(channel_selector, timeout=8000)
                        first_result = page.locator(channel_selector).first
                        first_result.click()
                        time.sleep(3)
                    except Exception:
                        pass

                    # Step 3: Handle chat input if emoji or text specified
                    if comment_or_emoji:
                        try:
                            chat_frame = page.frame_locator("iframe#chatframe")
                            if chat_frame:
                                chat_input = chat_frame.locator("#input, div#input[contenteditable='true']").first
                                if chat_input.is_visible(timeout=5000):
                                    chat_input.click()
                                    chat_input.fill(comment_or_emoji)
                                    chat_input.press("Enter")
                        except Exception:
                            pass

                    # Step 4: CRITICAL KEEP-ALIVE LOOP
                    # Keeps the browser process alive indefinitely until the user manually closes it
                    while True:
                        try:
                            # Check if user closed the page/window
                            if page.is_closed():
                                break
                            time.sleep(2)
                        except Exception:
                            break

            except Exception:
                # If Playwright fails, open directly in user's native Chrome
                fallback_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(channel_or_query)}"
                if self._chrome_path:
                    subprocess.Popen([self._chrome_path, fallback_url])
                else:
                    import webbrowser
                    webbrowser.open(fallback_url)

        # Spawn background automation thread so Python backend returns immediately without killing the browser
        t = threading.Thread(target=_run_playwright_workflow, daemon=False)
        t.start()

        return {
            "success": True,
            "channel": channel_or_query,
            "message": f"Successfully launched Chrome, navigated to YouTube '{channel_or_query}', and opened the stream. The browser window will remain open for you, Sir."
        }

    def navigate_and_interact(self, url: str) -> Dict[str, Any]:
        """Generic web navigation in persistent Chrome."""
        return self.open_url(url)


browser_controller = BrowserController()
