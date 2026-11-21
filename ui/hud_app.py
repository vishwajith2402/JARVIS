"""
Desktop HUD Application for JARVIS.
Wraps the tactical desktop AI dashboard in a native desktop window via pywebview.
Provides Python-to-JS bridge API for telemetry, speech, tools, and brain communication.
"""

import sys
from pathlib import Path
from typing import Any, Dict
import webview
from config.config_manager import config
from core.brain import brain
from core.telemetry import telemetry
from core.planner import planner
from core.updater import updater
from voice.speaker import speaker
from voice.listener import listener
from automation.app_controller import app_controller
from automation.file_manager import file_manager
from automation.system_control import system_control
from vision.visual_analyzer import visual_analyzer

STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_HTML = STATIC_DIR / "index.html"


class JarvisApiBridge:
    def __init__(self):
        self.auto_speak = config.get("voice", "auto_speak_responses", True)

    def get_telemetry(self) -> Dict[str, Any]:
        return telemetry.get_full_telemetry()

    def process_user_message(self, message: str) -> str:
        reply = brain.generate_response(message)
        if self.auto_speak:
            speaker.speak(reply)
        return reply

    def listen_voice(self) -> str:
        text = listener.listen_once(timeout=5.0)
        return text or ""

    def check_for_updates(self) -> Dict[str, Any]:
        return updater.check_git_updates()

    def apply_update(self) -> Dict[str, Any]:
        return updater.apply_git_update()

    def set_auto_speak(self, enabled: bool) -> None:
        self.auto_speak = enabled
        config.set("voice", "auto_speak_responses", enabled)

    def test_voice_synthesis(self) -> str:
        msg = f"Audio channels verified, {config.get('system', 'user_title', 'Sir')}. Voice synthesizer is fully functional."
        speaker.speak(msg)
        return msg

    def switch_model(self, model_name: str) -> Dict[str, Any]:
        """Hot-swap the active reasoning model on the fly."""
        brain.primary_model = model_name
        config.set("agent", "primary_model", model_name)
        return {"success": True, "active_model": model_name}

    def trigger_quick_action(self, action_type: str) -> str:
        if action_type == "open_vscode":
            res = app_controller.launch_app("vscode")
            msg = res.get("message", res.get("error", "Action completed."))
            if self.auto_speak:
                speaker.speak("Opening Visual Studio Code for you.")
            return msg

        elif action_type == "scan_projects":
            res = planner.plan_and_execute_project_inspection()
            if res.get("success"):
                proj = res.get("project_name")
                msg = f"Located your project '{proj}' and opened it in Visual Studio Code, Sir."
            else:
                msg = res.get("message", "Project search complete.")
            if self.auto_speak:
                speaker.speak(msg)
            return msg

        elif action_type == "screen_capture":
            res = visual_analyzer.analyze_screen()
            msg = res.get("response", res.get("error", "Vision scan complete."))
            if self.auto_speak:
                speaker.speak("Screen capture and optical scan complete, Sir.")
            return msg

        elif action_type == "lock_pc":
            system_control.lock_workstation()
            return "Workstation locked for your security, Sir."

        elif action_type == "check_updates":
            res = updater.check_git_updates()
            if res.get("has_update"):
                return f"Update available, Sir: {res.get('message')}. Applying git pull..."
            elif "error" in res:
                return f"Update status: {res.get('error')}"
            return "All JARVIS subsystems and features are running the latest version, Sir."

        return f"Unknown quick action: {action_type}"


def run_hud():
    """Launch the HUD desktop window."""
    api = JarvisApiBridge()
    window = webview.create_window(
        title="J.A.R.V.I.S. // Desktop Tactical AI Core",
        url=str(INDEX_HTML.resolve()),
        js_api=api,
        width=1280,
        height=820,
        resizable=True,
        min_size=(960, 600),
        background_color="#050a14"
    )
    webview.start(debug=False)


if __name__ == "__main__":
    run_hud()
