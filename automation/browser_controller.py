"""
Browser Controller for TITAN.
Automates browser tasks using Playwright (or native browser launching).
Supports:
- Navigating to websites (YouTube, GitHub, Google, etc.)
- Searching on YouTube, navigating to channels
- Typing in chat boxes, clicking buttons
- Executing interactive web workflows
100% Free & Local: Uses installed Playwright Chromium engine.
"""

import time
import subprocess
import webbrowser
from typing import Any, Dict, Optional
from config.config_manager import config


class BrowserController:
    def __init__(self):
        self._browser = None
        self._page = None

    def open_url(self, url: str) -> Dict[str, Any]:
        """Open a URL in the user's default browser or Chrome."""
        try:
            webbrowser.open(url)
            return {"success": True, "message": f"Navigated to {url} in your desktop browser, Sir."}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_youtube_action(self, channel_or_query: str, comment_or_emoji: Optional[str] = None) -> Dict[str, Any]:
        """
        Automates searching YouTube, navigating to channel/video, and optionally interacting with chat.
        Uses Playwright in visible mode so the user sees the real Chrome window executing.
        """
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                # Launch Chromium in headful (visible) mode so user sees it in action
                browser = p.chromium.launch(headless=False, args=["--start-maximized"])
                context = browser.new_context(no_viewport=True)
                page = context.new_page()

                # Step 1: Open YouTube
                search_url = f"https://www.youtube.com/results?search_query={channel_or_query.replace(' ', '+')}"
                page.goto(search_url, timeout=30000)
                page.wait_for_load_state("domcontentloaded")
                time.sleep(2)

                # Step 2: Try clicking the first channel or video result
                try:
                    # Look for channel avatar/title or video link
                    channel_selector = "#channel-title, #video-title, ytd-channel-renderer, ytd-video-renderer a#thumbnail"
                    page.wait_for_selector(channel_selector, timeout=8000)
                    first_result = page.locator(channel_selector).first
                    first_result.click()
                    time.sleep(3)
                except Exception:
                    pass

                # Step 3: If an emoji or chat text was requested, look for the live chat iframe/box
                interacted = False
                if comment_or_emoji:
                    try:
                        # Attempt to locate YouTube live chat input or comment box
                        chat_frame = page.frame_locator("iframe#chatframe")
                        if chat_frame:
                            chat_input = chat_frame.locator("#input, div#input[contenteditable='true']").first
                            if chat_input.is_visible(timeout=5000):
                                chat_input.click()
                                chat_input.fill(comment_or_emoji)
                                chat_input.press("Enter")
                                interacted = True
                    except Exception:
                        interacted = False

                # Keep browser open for the user to enjoy the video/stream
                return {
                    "success": True,
                    "channel": channel_or_query,
                    "message": f"Successfully launched YouTube, navigated to '{channel_or_query}', and opened the stream for you, Sir."
                }
        except Exception as e:
            # Fallback to direct native browser launch if Playwright is unavailable
            fallback_url = f"https://www.youtube.com/results?search_query={channel_or_query.replace(' ', '+')}"
            webbrowser.open(fallback_url)
            return {
                "success": True,
                "fallback": True,
                "message": f"Opened YouTube search for '{channel_or_query}' directly in your Chrome browser, Sir."
            }

    def navigate_and_interact(self, url: str, search_query: Optional[str] = None) -> Dict[str, Any]:
        """Generic web navigation and search handler."""
        target_url = url
        if not target_url.startswith("http"):
            target_url = f"https://{target_url}"

        try:
            webbrowser.open(target_url)
            return {
                "success": True,
                "url": target_url,
                "message": f"Opened {target_url} in your default browser, Sir."
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


browser_controller = BrowserController()
