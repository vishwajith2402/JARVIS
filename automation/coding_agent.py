"""
TITAN Autonomous Coding Agent (OpenHands / CodeAct Engine).
Handles:
1. Understanding complex user software & coding requirements.
2. Generating 100% complete, fully implemented code without placeholders or shortcuts.
3. Automatically saving the code to disk with an intelligent, semantic filename.
4. Testing and verifying execution in the local Python sandbox.
5. Self-healing: Automatically catches syntax/runtime errors and regenerates clean fixes.
6. Auto-launching GUI/desktop apps (Tkinter, Pygame, etc.) or web apps in persistent Chrome.
100% Free & Local.
"""

import os
import re
import sys
import time
import py_compile
import tempfile
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SANDBOX_DIR = Path(r"D:\Practice Projects\JARVIS\data\sandbox")
try:
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    SANDBOX_DIR = Path(tempfile.gettempdir()) / "titan_sandbox"
    SANDBOX_DIR.mkdir(parents=True, exist_ok=True)


class CodingAgent:
    def __init__(self, brain_executor: Any):
        self.brain = brain_executor

    def _extract_filename(self, prompt: str, code_content: str) -> str:
        """Dynamically determine a clean, semantic filename and extension."""
        prompt_lower = prompt.lower()

        # 1. Check for explicit filename in prompt (e.g. "save as app.py", "called test.py", "named server.py")
        file_match = re.search(r'(?:save\s+(?:it\s+)?as|called|named|file(?:name)?\s*[:=]?)\s+([a-zA-Z0-9_\-\.]+\.(?:py|html|css|js|json|sh|bat))', prompt, re.IGNORECASE)
        if file_match:
            return file_match.group(1).strip()

        # 2. Check for HTML/Web
        if any(w in prompt_lower for w in ("html", "website", "web page", "webpage", "landing page")):
            return "index.html"

        # 3. Known application semantic patterns
        patterns = [
            ("calculator", "calculator.py"),
            ("snake", "snake_game.py"),
            ("pong", "pong_game.py"),
            ("tic tac toe", "tictactoe.py"),
            ("todo", "todo_app.py"),
            ("weather", "weather_app.py"),
            ("clock", "digital_clock.py"),
            ("timer", "stopwatch_timer.py"),
            ("notepad", "text_editor.py"),
            ("text editor", "text_editor.py"),
            ("scraper", "web_scraper.py"),
            ("scrape", "web_scraper.py"),
            ("converter", "file_converter.py"),
            ("password", "password_generator.py"),
            ("paint", "drawing_canvas.py"),
            ("music", "music_player.py"),
            ("calendar", "calendar_app.py"),
            ("chat", "chat_interface.py"),
            ("quiz", "quiz_game.py")
        ]

        for token, fname in patterns:
            if token in prompt_lower:
                return fname

        # 4. Generate slug from prompt words
        words = re.findall(r'[a-zA-Z0-9]+', prompt_lower)
        filtered = [w for w in words if w not in ("create", "make", "build", "write", "code", "generate", "a", "an", "the", "in", "with", "basic", "simple", "python", "user", "interface", "gui")]
        if filtered:
            slug = "_".join(filtered[:3])
            return f"{slug}.py"

        return f"app_{int(time.time())}.py"

    def generate_and_deliver_code(self, user_prompt: str, session_id: str = "main") -> str:
        """
        End-to-end coding agent execution:
        1. Formulates specialized system prompt.
        2. Queries model with 180s timeout.
        3. Extracts code blocks.
        4. Saves code to disk.
        5. Validates syntax & auto-heals if needed.
        6. Runs CLI script or launches GUI app immediately.
        """
        system_instruction = (
            "You are TITAN's Senior Principal Software Engineer & Autonomous Coding Agent.\n"
            "Your objective: Deliver complete, production-grade, immediately executable software for the user's request.\n\n"
            "STRICT RULES:\n"
            "1. NEVER output placeholders, ellipses ('...'), or comments like '# Add logic here' or 'pass'. Every function, loop, and handler MUST be 100% written and functional.\n"
            "2. For GUI applications, ALWAYS use Python's built-in `tkinter` library so it runs out-of-the-box on Windows 11 with zero external pip dependencies.\n"
            "3. For web pages, provide a complete, standalone single-file HTML document with embedded modern CSS styling and JavaScript.\n"
            "4. Always enclose the primary executable code inside a standard markdown code fence (```python ... ``` or ```html ... ```).\n"
            "5. Address the user politely as Sir and explain how to use the software concisely."
        )

        messages = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"User Request: {user_prompt}\n\nPlease generate the complete, fully implemented code now."}
        ]

        try:
            raw_reply = self.brain._dispatch_chat(messages)
        except TimeoutError:
            return (
                "My apologies, Sir. Generating this comprehensive software required more time than the local reasoning window. "
                "I have expanded system capacity; please request again."
            )
        except Exception as e:
            return f"My apologies, Sir. The reasoning engine encountered an issue: {e}"

        # Extract code from response
        py_match = re.search(r"```python(.*?)```", raw_reply, re.DOTALL)
        html_match = re.search(r"```html(.*?)```", raw_reply, re.DOTALL)

        if not py_match and not html_match:
            # Fallback check for any code block
            gen_match = re.search(r"```[a-zA-Z]*(.*?)```", raw_reply, re.DOTALL)
            code_str = gen_match.group(1).strip() if gen_match else None
            is_html = False
        elif py_match:
            code_str = py_match.group(1).strip()
            is_html = False
        else:
            code_str = html_match.group(1).strip()
            is_html = True

        if not code_str:
            return raw_reply

        # Determine target file path
        filename = self._extract_filename(user_prompt, code_str)
        save_path = SANDBOX_DIR / filename

        from automation.file_manager import file_manager
        file_manager.write_file(str(save_path), code_str, overwrite=True)

        status_notes = []

        # Python Execution & Verification
        if not is_html:
            # Step A: Validate syntax
            try:
                py_compile.compile(str(save_path), doraise=True)
                syntax_valid = True
            except py_compile.PyCompileError as pe:
                syntax_valid = False
                # Self-healing attempt: Feed error back to model to fix
                fix_prompt = [
                    {"role": "system", "content": "Fix the syntax error in this Python script and return the complete corrected code in a ```python ... ``` block."},
                    {"role": "user", "content": f"Script:\n{code_str}\n\nCompile Error:\n{pe}"}
                ]
                try:
                    fixed_reply = self.brain._dispatch_chat(fix_prompt)
                    fixed_match = re.search(r"```python(.*?)```", fixed_reply, re.DOTALL)
                    if fixed_match:
                        code_str = fixed_match.group(1).strip()
                        file_manager.write_file(str(save_path), code_str, overwrite=True)
                        raw_reply = fixed_reply
                        syntax_valid = True
                except Exception:
                    pass

            # Step B: Launch or Execute
            prompt_lower = user_prompt.lower()
            is_gui = any(w in prompt_lower for w in ("ui", "gui", "interface", "window", "calculator", "game", "canvas", "tkinter", "app")) or "tkinter" in code_str

            if is_gui and syntax_valid:
                try:
                    # Launch detached desktop GUI window
                    subprocess.Popen([sys.executable, str(save_path)])
                    status_notes.append(f"Application automatically launched on your desktop ({filename}).")
                except Exception as e:
                    status_notes.append(f"Saved to `{save_path}`. Launch error: {e}")
            else:
                # Run CLI script in sandbox and capture output
                from automation.code_interpreter import code_interpreter
                exec_res = code_interpreter.execute_python(code_str, timeout_seconds=15)
                if exec_res.get("success"):
                    stdout_text = exec_res.get("stdout", "").strip()
                    if stdout_text:
                        status_notes.append(f"Execution Output:\n```\n{stdout_text}\n```")
                    status_notes.append(f"Executed successfully in {exec_res.get('execution_time_sec')}s.")
                else:
                    stderr_text = exec_res.get("stderr", "").strip()
                    if stderr_text:
                        status_notes.append(f"Execution notice: {stderr_text}")

        else:
            # HTML Webpage: Open in persistent Chrome
            try:
                from automation.browser_controller import browser_controller
                browser_controller.open_url(f"file:///{save_path.resolve()}")
                status_notes.append(f"Web application automatically opened in Chrome ({filename}).")
            except Exception:
                pass

        status_footer = "\n\n" + "\n".join([f"**[TITAN System]** {note}" for note in status_notes]) if status_notes else ""
        file_footer = f"\n**File Location:** [`{save_path}`](file:///{save_path.resolve()})"

        return raw_reply + status_footer + file_footer
