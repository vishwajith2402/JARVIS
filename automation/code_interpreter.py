"""
Code Interpreter Tool for TITAN (OpenJarvis Parity).
Executes Python scripts, data computations, and system tasks in a local sandbox.
Captures stdout, stderr, execution time, and generated artifacts.
100% Free & Local.
"""

import sys
import io
import time
import tempfile
import traceback
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

def _get_sandbox_dir() -> Path:
    candidates = [
        Path(r"D:\Practice Projects\JARVIS\data\sandbox"),
        Path.home() / ".titan" / "sandbox",
        Path(tempfile.gettempdir()) / "titan_sandbox"
    ]
    for c in candidates:
        try:
            c.mkdir(parents=True, exist_ok=True)
            test_file = c / ".test_write"
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink(missing_ok=True)
            return c
        except Exception:
            continue
    return Path(tempfile.gettempdir())

WORKSPACE_DIR = _get_sandbox_dir()


class CodeInterpreter:
    def __init__(self, workspace: Path = WORKSPACE_DIR):
        self.workspace = workspace

    def execute_python(self, code: str, timeout_seconds: int = 30) -> Dict[str, Any]:
        """
        Executes a Python code snippet inside a dedicated subprocess.
        Captures stdout, stderr, exit code, and return values.
        """
        script_file = self.workspace / f"script_{int(time.time() * 1000)}.py"
        try:
            with open(script_file, "w", encoding="utf-8") as f:
                f.write(code)

            start_time = time.time()
            process = subprocess.Popen(
                [sys.executable, str(script_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.workspace),
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            try:
                stdout, stderr = process.communicate(timeout=timeout_seconds)
                exec_time = round(time.time() - start_time, 3)
                success = (process.returncode == 0)

                return {
                    "success": success,
                    "returncode": process.returncode,
                    "stdout": stdout.strip(),
                    "stderr": stderr.strip(),
                    "execution_time_sec": exec_time,
                    "script_path": str(script_file)
                }
            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    "success": False,
                    "returncode": -1,
                    "stdout": "",
                    "stderr": f"Execution timed out after {timeout_seconds} seconds.",
                    "execution_time_sec": timeout_seconds,
                    "script_path": str(script_file)
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def execute_shell(self, command: str, timeout_seconds: int = 30) -> Dict[str, Any]:
        """
        Executes a safe PowerShell command inside the workspace directory.
        """
        start_time = time.time()
        try:
            process = subprocess.Popen(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.workspace),
                text=True,
                encoding="utf-8",
                errors="replace"
            )

            try:
                stdout, stderr = process.communicate(timeout=timeout_seconds)
                exec_time = round(time.time() - start_time, 3)
                return {
                    "success": (process.returncode == 0),
                    "returncode": process.returncode,
                    "stdout": stdout.strip(),
                    "stderr": stderr.strip(),
                    "execution_time_sec": exec_time
                }
            except subprocess.TimeoutExpired:
                process.kill()
                return {
                    "success": False,
                    "returncode": -1,
                    "stdout": "",
                    "stderr": f"Command timed out after {timeout_seconds} seconds.",
                    "execution_time_sec": timeout_seconds
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }


code_interpreter = CodeInterpreter()
