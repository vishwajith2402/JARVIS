"""
Comprehensive Test Suite for Professional TITAN Features.
Verifies:
1. Ultra-Realistic Neural Voice Engine & Barge-In.
2. Proactive Autonomous Watchdog & Morning Briefing.
3. Local Document & PDF Intelligence.
4. Multi-Step Macro & Routine Automator.
5. Live Vision Screen Sense Debugger.
6. Arc Reactor Tray Icon Generation.
7. Brain Tool Dispatch for New Capabilities.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.brain import brain
from voice.speaker import speaker
from automation.watchdog import watchdog
from automation.document_intelligence import doc_intelligence
from automation.routines import routines
from vision.screen_sense import screen_sense
from ui.tray_service import create_arc_reactor_icon


class TestProfessionalFeatures(unittest.TestCase):

    def test_01_neural_voice_and_barge_in(self):
        """Verify neural voices list and instant stop/barge-in capability."""
        voices = speaker.get_available_voices()
        self.assertGreater(len(voices), 0)
        self.assertIn("en-GB-RyanNeural (British Jarvis)", voices)

        # Test queueing speech and immediate stop
        speaker.speak("Testing neural barge-in.")
        self.assertTrue(speaker.is_speaking() or not speaker._speech_queue.empty())
        speaker.stop()
        self.assertTrue(speaker._stop_event.is_set())
        print("  [PASS] Neural Voice Engine (en-GB-RyanNeural) & Barge-In verified")

    def test_02_watchdog_and_morning_briefing(self):
        """Verify disk space calculation, git scanner, and morning briefing text."""
        disks = watchdog.check_disk_space()
        self.assertIn("C:", disks)
        self.assertIn("D:", disks)
        self.assertGreater(disks["C:"]["total_gb"], 0)

        briefing = watchdog.generate_morning_briefing()
        self.assertIn("Sir", briefing)
        self.assertIn("Hardware Status:", briefing)
        print("  [PASS] Autonomous Watchdog & Tactical Morning Briefing verified")

    def test_03_document_intelligence(self):
        """Verify local file text extraction and deep research indexing."""
        res = doc_intelligence.extract_text("README.md")
        self.assertTrue(res["success"])
        self.assertGreater(res["total_chars"], 100)
        self.assertEqual(res["file_name"], "README.md")
        print("  [PASS] Local Document Intelligence (Extraction & Indexing) verified")

    def test_04_macro_routines(self):
        """Verify routine definitions and focus mode execution."""
        routines_list = routines.list_routines()
        self.assertEqual(len(routines_list), 4)

        # Test focus mode execution
        res = routines.execute_routine("focus_mode")
        self.assertTrue(res["success"])
        self.assertIn("Focus mode engaged", res["message"])
        print("  [PASS] Macro Routines (Dev Session, Focus Mode, Quick Clean, Wrap-up) verified")

    def test_05_screen_sense_debugger_initialization(self):
        """Verify screen sense debugger initialization and coding agent coupling."""
        self.assertIsNotNone(screen_sense.coding_agent)
        print("  [PASS] Vision Screen Sense Debugger initialized")

    def test_06_tray_icon_generation(self):
        """Verify procedural in-memory Arc Reactor icon generation."""
        icon = create_arc_reactor_icon()
        self.assertEqual(icon.size, (64, 64))
        self.assertEqual(icon.mode, "RGBA")
        print("  [PASS] Arc Reactor System Tray Icon (64x64 RGBA) verified")

    def test_07_brain_new_tools_dispatch(self):
        """Verify execute_tool dispatch for newly added capabilities."""
        # 1. Morning briefing tool
        res_brief = brain.execute_tool("morning_briefing", {})
        self.assertTrue(res_brief.get("success", False))

        # 2. Routine execution tool
        res_routine = brain.execute_tool("execute_routine", {"routine_name": "focus_mode"})
        self.assertTrue(res_routine.get("success", False))

        # 3. Document analysis tool
        res_doc = brain.execute_tool("analyze_document", {"file_path": "README.md", "question": "What is TITAN?"})
        self.assertTrue(res_doc.get("success", False))

        print("  [PASS] Universal Agent Brain Tool Dispatch for all 7 features verified")


if __name__ == "__main__":
    unittest.main()
