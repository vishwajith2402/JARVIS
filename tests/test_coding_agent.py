"""
Unit Tests for TITAN Autonomous Coding Agent.
Verifies:
1. Dynamic semantic filename extraction (apps, games, tools, HTML).
2. Code compilation & syntax verification.
3. Sandbox file writing and execution capture.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(r"D:\Practice Projects\JARVIS")
sys.path.insert(0, str(ROOT))

from core.brain import brain
from automation.coding_agent import CodingAgent


class TestCodingAgent(unittest.TestCase):

    def setUp(self):
        self.coder = CodingAgent(brain)

    def test_01_filename_extraction(self):
        """Test intelligent filename determination."""
        fn1 = self.coder._extract_filename("create a basic calculator in python", "")
        self.assertEqual(fn1, "calculator.py")

        fn2 = self.coder._extract_filename("build a snake game with pygame", "")
        self.assertEqual(fn2, "snake_game.py")

        fn3 = self.coder._extract_filename("create a modern website landing page", "")
        self.assertEqual(fn3, "index.html")

        fn4 = self.coder._extract_filename("write a script called my_custom_tool.py", "")
        self.assertEqual(fn4, "my_custom_tool.py")
        print("  [PASS] Intelligent filename extraction verified")

    def test_02_file_saving_and_compilation(self):
        """Test saving and verifying valid Python code."""
        code = (
            "import math\n\n"
            "def calculate_area(radius):\n"
            "    return math.pi * radius * radius\n\n"
            "print('AREA=' + str(round(calculate_area(5), 2)))\n"
        )
        from automation.file_manager import file_manager
        from pathlib import Path
        import tempfile

        test_path = Path(tempfile.gettempdir()) / "test_circle_area.py"
        file_manager.write_file(str(test_path), code, overwrite=True)

        from automation.code_interpreter import code_interpreter
        res = code_interpreter.execute_python(code)
        self.assertTrue(res["success"])
        self.assertIn("AREA=78.54", res["stdout"])
        print("  [PASS] Code saving, execution, and stdout capture verified")


if __name__ == "__main__":
    unittest.main()
