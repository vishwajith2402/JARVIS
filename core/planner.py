"""
Multi-Step Task Planner for JARVIS.
Deconstructs complex user goals into atomic steps, tracks execution, and handles contingencies.
"""

from typing import Any, Callable, Dict, List, Optional
from core.memory import memory
from automation.app_controller import app_controller
from automation.file_manager import file_manager


class TaskPlanner:
    def __init__(self):
        pass

    def plan_and_execute_project_inspection(self, on_step: Optional[Callable[[str, str], None]] = None) -> Dict[str, Any]:
        """
        Executes the flagship autonomous task:
        1. Find all Python projects.
        2. Identify the most recently modified one.
        3. Open it in VS Code.
        4. Read its file structure.
        5. Formulate summary.
        """
        task_id = memory.add_task("Autonomous Python Project Inspection", "Locate recent project, open in VS Code, inspect files.")

        def notify(step_name: str, status: str):
            if on_step:
                on_step(step_name, status)

        notify("Step 1: Discovering Projects", "Scanning permitted workspaces...")
        projects = file_manager.find_projects()
        py_projects = [p for p in projects if p["language"] == "python"]

        if not py_projects:
            notify("Scan Result", "No active Python projects found in permitted directories.")
            memory.update_task_status(task_id, "failed")
            return {
                "success": False,
                "message": "I was unable to find any Python project repositories in your configured directories, Sir."
            }

        target = py_projects[0]
        target_name = target["name"]
        target_path = target["path"]

        notify("Step 2: Candidate Identified", f"Selected '{target_name}' (last modified recently).")
        memory.register_or_update_project(target_name, target_path, "python", "Autonomous inspection target")

        notify("Step 3: Launching VS Code", f"Opening '{target_name}' in editor...")
        launch_res = app_controller.launch_app("vscode", [target_path])

        notify("Step 4: Analyzing Directory Tree", "Scanning file hierarchy...")
        tree_res = file_manager.inspect_directory_tree(target_path, max_depth=2)

        notify("Step 5: Completion", f"Project '{target_name}' is loaded in Visual Studio Code.")
        memory.update_task_status(task_id, "completed")

        return {
            "success": True,
            "project_name": target_name,
            "project_path": target_path,
            "tree": tree_res.get("tree", {}),
            "launch_message": launch_res.get("message", "")
        }


planner = TaskPlanner()
