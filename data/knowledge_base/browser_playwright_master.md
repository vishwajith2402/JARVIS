# Browser Automation & Web Scraping Master Guide (Playwright)

## Core Principles
1. Use `sync_playwright` with persistent contexts (`launch_persistent_context`) so cookies, logins, and dark themes persist across runs.
2. Prevent unexpected browser closures: Keep browser alive in a background thread with an event loop monitoring `page.is_closed()`.
3. Wait conditions: Always wait for `domcontentloaded` or explicit selector visibility before clicking or typing.
4. Robust selector hierarchy: Use role selectors, text selectors, and CSS fallbacks.

## Template: Persistent Chrome Automation
```python
from playwright.sync_api import sync_playwright
import time
from pathlib import Path

def run_browser_task(url, actions_callback=None):
    profile_dir = Path.home() / ".titan" / "browser_profile"
    profile_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            args=["--start-maximized", "--no-default-browser-check"],
            no_viewport=True
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(url, timeout=40000)
        page.wait_for_load_state("domcontentloaded")

        if actions_callback:
            actions_callback(page)

        # Keep alive until user closes window
        while not page.is_closed():
            time.sleep(2)
```

## Template: YouTube Navigation & Live Chat Interaction
```python
def interact_with_youtube_live(page, channel_name, emoji="😊"):
    # 1. Search channel
    page.goto(f"https://www.youtube.com/results?search_query={channel_name}")
    page.wait_for_selector("ytd-channel-renderer, ytd-video-renderer", timeout=8000)

    # 2. Click live stream or channel
    live_badge = page.locator("ytd-video-renderer:has-text('LIVE')").first
    if live_badge.is_visible():
        live_badge.click()
    else:
        page.locator("#channel-title").first.click()

    # 3. Enter Live Chat
    try:
        chat_frame = page.frame_locator("iframe#chatframe")
        chat_box = chat_frame.locator("#input, div#input[contenteditable='true']").first
        if chat_box.is_visible(timeout=5000):
            chat_box.click()
            chat_box.fill(emoji)
            chat_box.press("Enter")
    except Exception:
        pass
```
