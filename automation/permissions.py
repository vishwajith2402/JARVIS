"""
Permission Guardrails for JARVIS.
Enforces 3-tier security model:
- Level 1: Automatic execution (safe, read-only, telemetry, queries)
- Level 2: Confirmation required (file creation/editing, launching apps)
- Level 3: Strictly restricted / explicit approval (deletions, process termination, shell commands)
"""

from enum import Enum
from typing import Any, Callable, Dict, Optional
from config.config_manager import config


class PermissionLevel(Enum):
    LEVEL_1_AUTO = 1
    LEVEL_2_CONFIRM = 2
    LEVEL_3_RESTRICTED = 3


class PermissionManager:
    def __init__(self):
        self._action_levels: Dict[str, PermissionLevel] = {
            # Level 1
            "get_system_stats": PermissionLevel.LEVEL_1_AUTO,
            "list_files": PermissionLevel.LEVEL_1_AUTO,
            "read_file": PermissionLevel.LEVEL_1_AUTO,
            "search_files": PermissionLevel.LEVEL_1_AUTO,
            "list_windows": PermissionLevel.LEVEL_1_AUTO,
            "web_search": PermissionLevel.LEVEL_1_AUTO,
            "inspect_project": PermissionLevel.LEVEL_1_AUTO,

            # Level 2
            "open_application": PermissionLevel.LEVEL_2_CONFIRM,
            "create_file": PermissionLevel.LEVEL_2_CONFIRM,
            "edit_file": PermissionLevel.LEVEL_2_CONFIRM,
            "create_folder": PermissionLevel.LEVEL_2_CONFIRM,
            "take_screenshot": PermissionLevel.LEVEL_2_CONFIRM,

            # Level 3
            "delete_file": PermissionLevel.LEVEL_3_RESTRICTED,
            "delete_folder": PermissionLevel.LEVEL_3_RESTRICTED,
            "kill_process": PermissionLevel.LEVEL_3_RESTRICTED,
            "run_shell_command": PermissionLevel.LEVEL_3_RESTRICTED,
        }
        self.confirmation_callback: Optional[Callable[[str, str, Dict[str, Any]], bool]] = None

    def get_action_level(self, action_name: str) -> PermissionLevel:
        return self._action_levels.get(action_name, PermissionLevel.LEVEL_3_RESTRICTED)

    def is_permitted(self, action_name: str, details: Dict[str, Any]) -> bool:
        level = self.get_action_level(action_name)
        confirm_l2 = config.get("automation", "confirm_level_2", False)
        confirm_l3 = config.get("automation", "confirm_level_3", True)

        if level == PermissionLevel.LEVEL_1_AUTO:
            return True

        if level == PermissionLevel.LEVEL_2_CONFIRM:
            if not confirm_l2:
                return True
            if self.confirmation_callback:
                return self.confirmation_callback(action_name, f"Execute Level 2 operation: {action_name}", details)
            return False

        if level == PermissionLevel.LEVEL_3_RESTRICTED:
            if not confirm_l3:
                return True
            if self.confirmation_callback:
                return self.confirmation_callback(action_name, f"SECURITY WARNING: Level 3 Restricted action '{action_name}' requested.", details)
            return False

        return False


permissions = PermissionManager()
