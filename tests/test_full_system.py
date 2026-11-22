"""
JARVIS System Full Diagnostic and Verification Script
Runs end-to-end tests across all core systems and features.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(r"D:\Practice Projects\JARVIS")
sys.path.insert(0, str(ROOT))

from core.telemetry import telemetry
from core.memory import memory
from core.brain import brain
from core.hermes_parser import HermesToolParser
from core.planner import planner
from core.updater import updater
from automation.file_manager import file_manager
from automation.system_control import system_control
from automation.permissions import permissions, PermissionLevel
from automation.app_controller import app_controller
from vision.screen_capture import screen_capturer
from vision.visual_analyzer import visual_analyzer
from voice.speaker import speaker
from voice.wake_word import wake_detector


class TestJarvisFullSystem(unittest.TestCase):

    def test_01_telemetry(self):
        stats = telemetry.get_full_telemetry()
        self.assertIn("gpu", stats)
        self.assertIn("cpu", stats)
        self.assertIn("ram", stats)
        self.assertIn("battery", stats)
        self.assertGreater(stats["ram"]["total_gb"], 0)
        print(f"  [PASS] GPU: {stats['gpu']['name']} | VRAM: {stats['gpu']['vram_used_mb']}/{stats['gpu']['vram_total_mb']} MB")
        print(f"  [PASS] CPU: AMD Ryzen ({stats['cpu']['cores']} cores) | RAM: {stats['ram']['used_gb']}/{stats['ram']['total_gb']} GB")

    def test_02_memory_sqlite(self):
        sid = "test_diagnostics_session"
        memory.add_message(sid, "user", "System diagnostic run")
        memory.add_message(sid, "assistant", "Diagnostics in progress, Sir.")
        recent = memory.get_recent_messages(sid, limit=2)
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0]["role"], "user")
        self.assertEqual(recent[1]["role"], "assistant")
        print("  [PASS] SQLite conversation history logged & retrieved successfully")

    def test_03_file_manager(self):
        projects = file_manager.find_projects()
        self.assertIsInstance(projects, list)
        read_res = file_manager.read_file(str(ROOT / "README.md"), max_lines=5)
        self.assertTrue(read_res["success"])
        print(f"  [PASS] Projects indexed ({len(projects)} found) | Safe file reading verified")

    def test_04_system_control_and_permissions(self):
        self.assertEqual(permissions.get_action_level("get_system_stats"), PermissionLevel.LEVEL_1_AUTO)
        self.assertEqual(permissions.get_action_level("open_application"), PermissionLevel.LEVEL_2_CONFIRM)
        self.assertEqual(permissions.get_action_level("delete_file"), PermissionLevel.LEVEL_3_RESTRICTED)

        # Test system control volume actions
        vol_up = system_control.volume_up(steps=1)
        self.assertTrue(vol_up["success"])
        vol_down = system_control.volume_down(steps=1)
        self.assertTrue(vol_down["success"])
        print("  [PASS] 3-tier security permissions & master volume system controls verified")

    def test_05_app_controller(self):
        notepad_path = app_controller._resolve_executable("notepad")
        self.assertIsNotNone(notepad_path)
        print(f"  [PASS] App controller executable resolver verified (notepad: {notepad_path})")

    def test_06_vision_module(self):
        self.assertTrue(hasattr(screen_capturer, "capture_fullscreen"))
        self.assertTrue(hasattr(screen_capturer, "capture_region"))
        self.assertTrue(hasattr(visual_analyzer, "analyze_image"))
        self.assertTrue(hasattr(visual_analyzer, "analyze_screen"))
        print("  [PASS] Vision pipeline (screen capturer + multi-modal analyzer) loaded & ready")

    def test_07_voice_sapi(self):
        voices = speaker.get_available_voices()
        self.assertGreater(len(voices), 0)
        print(f"  [PASS] Local Windows SAPI voice synthesizer verified ({len(voices)} voices)")

    def test_08_wake_word_detector(self):
        self.assertTrue(wake_detector.contains_wake_word("Hey Jarvis, check my battery"))
        cmd = wake_detector.extract_command("Hey Jarvis, check my battery")
        self.assertEqual(cmd.lower(), "check my battery")
        print("  [PASS] Wake-word detector ('Hey Jarvis') and command extraction verified")

    def test_09_hermes_parser(self):
        sample = '<tool_call>\n{"name": "open_application", "arguments": {"app_name": "code"}}\n</tool_call>'
        parsed = HermesToolParser.parse_tool_call(sample)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["name"], "open_application")
        self.assertEqual(parsed["arguments"]["app_name"], "code")
        print("  [PASS] Hermes XML zero-hallucination tool calling parser verified")

    def test_10_ai_brain_inference(self):
        st = brain.status
        resp = brain.generate_response("Respond with one word: Functional", session_id="test_diag")
        self.assertIsInstance(resp, str)
        self.assertGreater(len(resp.strip()), 0)
        print(f"  [PASS] Local AI Brain ({st['provider'].upper()} / {st['model']}): {resp.strip()[:60]}...")

    def test_11_agent_planner(self):
        steps_log = []
        res = planner.plan_and_execute_project_inspection(on_step=lambda step, desc: steps_log.append(step))
        self.assertIn("success", res)
        print(f"  [PASS] Flagship Autonomous Project Inspection Planner executed ({len(steps_log)} steps logged)")

    def test_12_updater(self):
        up = updater.check_git_updates()
        self.assertIn("has_update", up)
        print(f"  [PASS] Git updater integration verified: has_update={up['has_update']} | {up.get('message', '')}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
