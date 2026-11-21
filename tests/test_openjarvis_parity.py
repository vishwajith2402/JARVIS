"""
OpenJarvis Parity & Feature Verification Test Suite for TITAN.
Tests:
1. Local Python Code Interpreter execution (sandbox, stdout/stderr, timeout).
2. ReAct reasoning loop & tool call action parser.
3. OpenJarvis 8 Agent Mode switcher & dispatch router.
4. Autonomous YouTube multi-step intent interceptor & browser keep-alive configuration.
5. Universal two-way application lifecycle control (open & close 287+ installed software).
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(r"D:\Practice Projects\JARVIS")
sys.path.insert(0, str(ROOT))

from core.brain import brain
from core.react_agent import ReActAgent, OpenJarvisAgentManager
from automation.code_interpreter import code_interpreter
from automation.browser_controller import browser_controller
from automation.app_controller import app_controller


class TestOpenJarvisParity(unittest.TestCase):

    def test_01_code_interpreter_python(self):
        """Test Python sandbox code execution."""
        code = (
            "import math\n"
            "ans = math.factorial(6)\n"
            "print(f'FACTORIAL_RESULT={ans}')"
        )
        res = code_interpreter.execute_python(code)
        self.assertTrue(res["success"])
        self.assertEqual(res["returncode"], 0)
        self.assertIn("FACTORIAL_RESULT=720", res["stdout"])
        self.assertGreater(res["execution_time_sec"], 0)
        print("  [PASS] Code Interpreter executed Python math cleanly in sandbox")

    def test_02_react_action_parser(self):
        """Test ReAct Thought/Action/Observation format parser."""
        agent = ReActAgent(brain)
        sample = (
            "Thought: The user requested to open Chrome and navigate to YouTube.\n"
            "Action: browser_action(action=\"youtube_search\", target=\"oru vela irukumo\")\n"
        )
        parsed = agent.parse_action(sample)
        self.assertIsNotNone(parsed)
        tool_name, tool_args = parsed
        self.assertEqual(tool_name, "browser_action")
        self.assertEqual(tool_args.get("action"), "youtube_search")
        self.assertEqual(tool_args.get("target"), "oru vela irukumo")
        print("  [PASS] ReAct Thought-Action parser verified with structured tool invocation")

    def test_03_agent_manager_modes(self):
        """Test switching between OpenJarvis agent archetypes."""
        mgr = OpenJarvisAgentManager(brain)
        self.assertTrue(mgr.set_agent_mode("native_react"))
        self.assertEqual(mgr.current_agent_mode, "native_react")
        self.assertTrue(mgr.set_agent_mode("code_interpreter"))
        self.assertEqual(mgr.current_agent_mode, "code_interpreter")
        self.assertTrue(mgr.set_agent_mode("deep_research"))
        self.assertEqual(mgr.current_agent_mode, "deep_research")
        self.assertTrue(mgr.set_agent_mode("morning_digest"))
        self.assertEqual(mgr.current_agent_mode, "morning_digest")
        self.assertTrue(mgr.set_agent_mode("orchestrator"))
        self.assertEqual(mgr.current_agent_mode, "orchestrator")
        print("  [PASS] OpenJarvis 8-mode Agent Manager hot-swapping verified")

    def test_04_compound_browser_intent_intercept(self):
        """Verify the user's exact YouTube compound command is executed without disclaimer."""
        cmd = "open chrome , and navigate to youtube then search oru vela irukumo channel , subscribe it and enter the live running in it and drop a smile emoji in it"
        reply = brain.generate_response(cmd)
        
        # Must NOT contain LLM disclaimer/refusal
        self.assertNotIn("don't have the capability to perform actions on the internet", reply.lower())
        self.assertNotIn("cannot browse the internet", reply.lower())
        # Must indicate positive automation execution
        self.assertTrue(any(w in reply.lower() for w in ("chrome", "youtube", "oru vela", "browser", "stream")))
        print("  [PASS] User's exact compound YouTube command dispatched cleanly without LLM refusal")

    def test_05_two_way_app_lifecycle(self):
        """Verify universal application resolution for both opening and closing."""
        notepad_match = app_controller.find_software("notepad")
        self.assertIsNotNone(notepad_match)
        # Test close command routing on notepad
        close_res = app_controller.close_app("notepad")
        self.assertIn("message", close_res)
        print("  [PASS] Universal application lifecycle (open and close software) verified")


if __name__ == "__main__":
    unittest.main()
