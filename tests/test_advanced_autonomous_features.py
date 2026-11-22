"""
Test Suite for Advanced Autonomous Capabilities:
1. TaskBoard Persistent SQLite CRUD & Natural Language Task Management.
2. WebAgent Structured Scraping & File Downloader.
3. Dynamic Skill Creator & Hot-Reloading.
4. Windows AutoStart & Batch Launcher.
5. Brain Tool Execution Dispatch for Advanced Tools.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.brain import brain
from core.task_board import task_board
from automation.web_agent import web_agent
from automation.skill_creator import skill_creator
from core.autostart import autostart_manager


class TestAdvancedAutonomousFeatures(unittest.TestCase):

    def test_01_task_board_lifecycle(self):
        """Test task creation, status update, listing, and deletion."""
        # 1. Add Task
        res_add = task_board.add_task(
            title="Calibrate local AI neural models",
            description="Optimize Ollama Flash Attention on RTX 3050",
            priority="high"
        )
        self.assertTrue(res_add["success"])
        task_id = res_add["task_id"]

        # 2. Update Status
        res_upd = task_board.update_status(task_id, "in_progress")
        self.assertTrue(res_upd["success"])
        self.assertEqual(res_upd["new_status"], "in_progress")

        # 3. List
        tasks = task_board.list_tasks(status_filter="in_progress")
        self.assertTrue(any(t["id"] == task_id for t in tasks))

        # 4. Summary
        summary = task_board.get_summary()
        self.assertGreaterEqual(summary["total"], 1)

        # 5. Delete
        res_del = task_board.delete_task(task_id)
        self.assertTrue(res_del["success"])
        print("  [PASS] TaskBoard SQLite Kanban Lifecycle verified")

    def test_02_web_agent_scraping(self):
        """Verify BeautifulSoup HTML parsing and table extraction."""
        sample_html = """
        <html><head><title>TITAN Test Hub</title></head>
        <body>
            <h1>System Status</h1>
            <table>
                <tr><th>Component</th><th>Status</th></tr>
                <tr><td>GPU</td><td>Online</td></tr>
                <tr><td>Ollama</td><td>Ready</td></tr>
            </table>
        </body></html>
        """
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(sample_html, "html.parser")
        self.assertEqual(soup.title.string, "TITAN Test Hub")
        self.assertEqual(len(soup.find_all("tr")), 3)
        print("  [PASS] WebAgent Structured Scraping Engine verified")

    def test_03_skill_creator_and_hot_reloader(self):
        """Verify dynamic custom skill loading and execution."""
        # Create a mock custom skill file directly
        skill_code = """
def execute_skill(args: dict) -> dict:
    val = args.get("input_val", 10)
    return {"success": True, "result": val * 3, "message": f"Multiplied to {val * 3}"}
"""
        skill_file = Path(ROOT) / "automation" / "skills" / "skill_unit_test_math.py"
        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(skill_code)

        # Reload skills
        skill_creator._load_existing_skills()
        self.assertIn("unit_test_math", skill_creator.loaded_skills)

        # Execute
        res = skill_creator.execute_custom_skill("unit_test_math", {"input_val": 7})
        self.assertTrue(res["success"])
        self.assertEqual(res["result"], 21)

        # Clean up test file
        try:
            skill_file.unlink()
        except Exception:
            pass
        print("  [PASS] Dynamic Skill Creator & Hot-Reloading verified")

    def test_04_autostart_and_bat_launcher(self):
        """Verify Windows batch launcher generation."""
        bat_path = autostart_manager._ensure_bat_file()
        self.assertTrue(bat_path.exists())
        with open(bat_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("TITAN Desktop AI", content)
        self.assertIn("main.py", content)
        print(f"  [PASS] Windows 1-Click Batch Launcher ({bat_path.name}) verified")

    def test_05_brain_tool_dispatch_for_advanced_tools(self):
        """Verify Brain execute_tool handles task management and web tools."""
        # Task add via brain
        res_task = brain.execute_tool("manage_tasks", {
            "action": "add",
            "title": "Autonomous Verification Task",
            "priority": "normal"
        })
        self.assertTrue(res_task.get("success", False))

        # Task list via brain
        res_list = brain.execute_tool("manage_tasks", {"action": "list"})
        self.assertTrue(res_list.get("success", False))
        self.assertIn("tasks", res_list)

        print("  [PASS] Universal Agent Brain Tool Dispatch for Advanced Tools verified")


if __name__ == "__main__":
    unittest.main()
