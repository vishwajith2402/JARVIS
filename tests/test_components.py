"""
Unit and integration test suite for JARVIS modules.
Tests Hermes parser, multi-engine brain, telemetry, permissions, and memory.
Run with: python tests/test_components.py
"""

import sys
import unittest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.telemetry import telemetry
from core.memory import memory
from core.brain import brain
from core.hermes_parser import HermesToolParser
from automation.permissions import permissions, PermissionLevel
from voice.wake_word import wake_detector


class TestJarvisCore(unittest.TestCase):

    def test_telemetry(self):
        stats = telemetry.get_full_telemetry()
        self.assertIn("gpu", stats)
        self.assertIn("cpu", stats)
        self.assertIn("ram", stats)
        self.assertIn("battery", stats)
        self.assertGreater(stats["ram"]["total_gb"], 0)

    def test_memory_conversations(self):
        session_id = "test_session"
        memory.add_message(session_id, "user", "Hello Jarvis", "greeting")
        memory.add_message(session_id, "assistant", "At your service, Sir.", "greeting")
        recent = memory.get_recent_messages(session_id, limit=2)
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0]["role"], "user")
        self.assertEqual(recent[1]["role"], "assistant")

    def test_permissions(self):
        self.assertEqual(permissions.get_action_level("get_system_stats"), PermissionLevel.LEVEL_1_AUTO)
        self.assertEqual(permissions.get_action_level("open_application"), PermissionLevel.LEVEL_2_CONFIRM)
        self.assertEqual(permissions.get_action_level("delete_file"), PermissionLevel.LEVEL_3_RESTRICTED)

    def test_wake_word(self):
        self.assertTrue(wake_detector.contains_wake_word("Hey Jarvis, what is my battery status?"))
        self.assertTrue(wake_detector.contains_wake_word("Jarvis open code"))
        self.assertFalse(wake_detector.contains_wake_word("What is the weather today?"))
        cmd = wake_detector.extract_command("Hey Jarvis, open VS Code")
        self.assertEqual(cmd.lower(), "open vs code")

    def test_hermes_parser(self):
        # 1. Test Hermes XML format
        xml_sample = """Certainly, Sir.
<tool_call>
{"name": "open_application", "arguments": {"app_name": "vscode"}}
</tool_call>
"""
        parsed = HermesToolParser.parse_tool_call(xml_sample)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["name"], "open_application")
        self.assertEqual(parsed["arguments"]["app_name"], "vscode")

        # 2. Test Markdown JSON fallback
        json_sample = """```json
{"tool": "find_projects", "args": {"root_dir": "D:\\Practice Projects"}}
```"""
        parsed_json = HermesToolParser.parse_tool_call(json_sample)
        self.assertIsNotNone(parsed_json)
        self.assertEqual(parsed_json["name"], "find_projects")

    def test_brain_status(self):
        st = brain.status
        self.assertIn("provider", st)
        self.assertIn("model", st)
        self.assertIn("is_online", st)


if __name__ == "__main__":
    unittest.main()
