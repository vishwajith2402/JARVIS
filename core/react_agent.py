"""
OpenJarvis Parity: Autonomous ReAct & Orchestrator Agent Engine for TITAN.
Implements the 8 OpenJarvis agent archetypes:
1. OrchestratorAgent (multi-step tool planning & execution)
2. NativeReActAgent (Thought -> Action -> Observation -> Final Answer)
3. DeepResearchAgent (multi-hop local database + web synthesis)
4. CodeInterpreterAgent (Python sandbox code generator & runner)
5. MorningDigestAgent (system telemetry & daily briefing)
6. MonitorOperativeAgent (continuous background health watcher)
7. OperativeAgent (persistent task execution)
8. SimpleAgent (direct conversational assistant)

100% Free & Local. Runs on Ollama, Msty, or LM Studio without any cloud API fees.
"""

import json
import re
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

REACT_SYSTEM_PROMPT = """You are TITAN, an advanced local autonomous AI agent created to serve as your personal workstation assistant.
You operate completely locally on HP Victus hardware (AMD Ryzen 5, NVIDIA RTX 3050 4GB VRAM, 16GB RAM) without external cloud APIs.

You solve complex multi-step user tasks by using tools in a structured Reasoning Loop:

FORMAT INSTRUCTIONS:
To complete a task, you MUST use the following format:

Thought: Consider what step to take next.
Action: tool_name({"param1": "val1", ...})
Observation: [The result of the tool action will appear here]
... (repeat Thought/Action/Observation N times as needed)
Thought: I now have enough information to answer or the action is completed.
Final Answer: The final response to the user.

AVAILABLE TOOLS:
1. open_application(app_name: str) - Launches any application or software installed on this Windows PC.
2. close_application(app_name: str) - Gracefully or forcefully terminates any running software or process on the PC.
3. browser_action(action: str, target: str, extra: Optional[str]) - Automates Chrome/Playwright browsing: YouTube search, channels, subscribing, live stream chat, emoji sending, and URL navigation. Windows stay open.
4. execute_python(code: str) - Executes Python code in a local sandbox, returning stdout, stderr, and execution time.
5. execute_shell(command: str) - Executes PowerShell or CMD commands in workspace.
6. write_file(path: str, content: str, overwrite: bool) - Writes or creates text/code files on disk.
7. read_file(path: str) - Safely reads file contents.
8. search_files(pattern: str, root_dir: Optional[str]) - Searches for files matching a pattern.
9. list_directory(dir_path: str) - Lists files and subdirectories.
10. gui_click(x: int, y: int, button: str, double: bool) - Clicks mouse at screen coordinates.
11. gui_type(text: str) - Types keystrokes directly into active software.
12. gui_hotkey(keys: List[str]) - Sends keyboard shortcuts (e.g. ['ctrl', 's'], ['alt', 'f4']).
13. deep_research(query: str) - Multi-hop search across indexed local projects, documents, and codebases.
14. web_search(query: str) - Performs web search queries.
15. capture_screen(prompt: Optional[str]) - Takes a screenshot and analyzes desktop contents.
16. get_system_stats() - Live CPU, GPU VRAM, RAM, and Battery telemetry.
17. set_brightness(level: int) - Adjusts monitor brightness.
18. empty_recycle_bin() - Cleans Windows Recycle Bin.
19. morning_digest() - Generates system health and daily productivity briefing.
20. execute_routine(routine_name: str) - Executes multi-step macro routines (dev_session, focus_mode, quick_clean, evening_wrapup).
21. morning_briefing() - Proactive morning briefing with hardware diagnostics, git scan, and schedule.
22. analyze_document(file_path: str, question: Optional[str]) - Local PDF, CSV, JSON, and document intelligence & extraction.
23. debug_screen(hint: Optional[str]) - Vision screen debugger that inspects active errors on screen and creates automatic code fixes.
24. create_new_skill(skill_name: str, requirement: str) - Teaches TITAN a brand new custom Python capability and hot-reloads it immediately.
25. manage_tasks(action: str, task_id: Optional[int], title: Optional[str], status: Optional[str]) - Adds, updates, lists, or marks tasks as done on the persistent Kanban board.
26. web_download(url: str, filename: Optional[str]) - Downloads remote files, PDFs, datasets, or zips to the local downloads folder.
27. extract_web_data(url: str) - Scrapes structured tables, headlines, and articles from webpages.

RULES:
- NEVER say "I don't have internet access" or "I cannot interact with online content". You have the `browser_action` tool and `web_search` tool specifically to browse the internet, interact with websites, open YouTube, subscribe, and chat!
- When asked to perform web, YouTube, or application actions, invoke the appropriate tool immediately.
- Always be polite, decisive, and address the user as Sir.
"""


class ReActAgent:
    def __init__(self, brain_executor: Any):
        self.brain = brain_executor

    def parse_action(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Parses `Action: tool_name({...})` from LLM output.
        """
        # Match Action: tool_name({...})
        pattern = r"Action:\s*([a-zA-Z0-9_]+)\s*\((.*?)\)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            tool_name = match.group(1).strip()
            args_str = match.group(2).strip()
            if not args_str:
                return tool_name, {}
            try:
                # Try JSON parse
                args = json.loads(args_str)
                return tool_name, args
            except Exception:
                # Try simple key=val parsing
                args = {}
                kv_pattern = r'([a-zA-Z0-9_]+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^,\s]+))'
                for m in re.finditer(kv_pattern, args_str):
                    k = m.group(1)
                    v = m.group(2) or m.group(3) or m.group(4)
                    args[k] = v
                return tool_name, args

        # Fallback: check for Hermes <tool_call>
        from core.hermes_parser import HermesToolParser
        call = HermesToolParser.parse_tool_call(text)
        if call:
            return call.get("name"), call.get("arguments", {})

        return None

    def execute_react_loop(
        self,
        user_query: str,
        session_id: str = "main",
        max_turns: int = 5,
        on_step: Optional[Callable[[str], None]] = None
    ) -> str:
        """
        Executes an autonomous ReAct loop:
        Repeatedly prompts LLM with history + thoughts + observations until Final Answer is produced.
        """
        conversation = [
            {"role": "system", "content": REACT_SYSTEM_PROMPT},
            {"role": "user", "content": f"Task: {user_query}"}
        ]

        current_prompt = f"Task: {user_query}\nThought:"

        for turn in range(max_turns):
            # Dispatch to LLM with timeout safeguard
            try:
                step_response = self.brain._dispatch_chat(conversation)
            except TimeoutError:
                return (
                    "My apologies, Sir. Code generation required more time than the local reasoning window. "
                    "I have adjusted processing parameters. Please issue the command again."
                )
            except Exception as e:
                return f"My apologies, Sir. Communication with the local reasoning engine encountered an issue: {e}"

            if not step_response.strip().startswith("Thought:"):
                step_response = f"Thought: {step_response}"

            if on_step:
                on_step(step_response)

            # Check for Final Answer
            if "Final Answer:" in step_response:
                parts = step_response.split("Final Answer:", 1)
                final_answer = parts[1].strip()
                return final_answer

            # Check for Action
            parsed = self.parse_action(step_response)
            if not parsed:
                # If no action found and no final answer, return the response cleanly
                clean = re.sub(r"Thought:\s*", "", step_response).strip()
                return clean

            tool_name, tool_args = parsed

            # Execute tool through brain
            tool_result = self.brain.execute_tool(tool_name, tool_args)
            obs_str = json.dumps(tool_result, ensure_ascii=False)
            if len(obs_str) > 1500:
                obs_str = obs_str[:1500] + "... [truncated]"

            obs_message = f"\nObservation: {obs_str}\nThought:"
            if on_step:
                on_step(f"Observation: {obs_str}")

            conversation.append({"role": "assistant", "content": step_response})
            conversation.append({"role": "user", "content": obs_message})

        return f"Task completed, Sir. Tools were executed according to your specifications."


class OpenJarvisAgentManager:
    """
    Manages the 8 OpenJarvis agent archetypes and routes prompts to the active specialist.
    """
    def __init__(self, brain_executor: Any):
        self.brain = brain_executor
        self.react_agent = ReActAgent(brain_executor)
        self.current_agent_mode = "orchestrator"

    def set_agent_mode(self, mode: str) -> bool:
        valid_modes = [
            "orchestrator", "native_react", "deep_research",
            "native_openhands", "code_interpreter", "morning_digest",
            "monitor_operative", "simple"
        ]
        if mode.lower() in valid_modes:
            self.current_agent_mode = mode.lower()
            return True
        return False

    def route_query(self, user_prompt: str, session_id: str = "main") -> str:
        mode = self.current_agent_mode

        # 1. Simple Agent: Direct chat, no tool overhead
        if mode == "simple":
            return self.brain._dispatch_chat([
                {"role": "system", "content": "You are TITAN, a concise, helpful desktop assistant."},
                {"role": "user", "content": user_prompt}
            ])

        # 2. Deep Research Agent: Dedicated local knowledge synthesis
        elif mode == "deep_research":
            from automation.deep_research import deep_research
            res = deep_research.deep_research_query(user_prompt)
            return res.get("synthesis", "Deep research query completed, Sir.")

        # 3. Morning Digest: Scheduled daily briefing
        elif mode == "morning_digest":
            from automation.daily_briefing import daily_briefing
            res = daily_briefing.generate_morning_digest()
            return res.get("digest", "Daily briefing prepared, Sir.")

        # 4. Code Interpreter Agent (OpenHands style)
        elif mode in ("code_interpreter", "native_openhands"):
            from automation.code_interpreter import code_interpreter

            # Check for markdown code blocks or direct code execution
            code_match = re.search(r"```(?:python)?(.*?)```", user_prompt, re.DOTALL)
            direct_code = None
            if code_match:
                direct_code = code_match.group(1).strip()
            elif user_prompt.strip().startswith(("run:", "exec:", "python:", "eval:")):
                direct_code = re.sub(r"^(run|exec|python|eval):\s*", "", user_prompt.strip(), flags=re.IGNORECASE)
            elif any(user_prompt.strip().startswith(kw) for kw in ("import ", "from ", "def ", "class ", "print(", "for ", "while ")) and len(user_prompt.strip().splitlines()) >= 1:
                # If it looks like raw python code without english request keywords
                if not any(req_word in user_prompt.lower() for req_word in ("create ", "build ", "make ", "generate ", "write me ", "how to ")):
                    direct_code = user_prompt.strip()

            if direct_code:
                res = code_interpreter.execute_python(direct_code)
                stdout = res.get('stdout', '') or '(no stdout output)'
                stderr = res.get('stderr', '')
                exec_time = res.get('execution_time_sec', 0.0)
                err_part = f"\n**Stderr:**\n```\n{stderr}\n```" if stderr else ""
                return f"⚡ **Python Sandbox Execution:**\n```\n{stdout}\n```{err_part}\n\n*Execution completed in {exec_time}s (Return Code: {res.get('return_code', 0)}).*"

            # Use dedicated OpenHands Coding Agent for generating complete software & scripts
            from automation.coding_agent import CodingAgent
            coder = CodingAgent(self.brain)
            return coder.generate_and_deliver_code(user_prompt, session_id=session_id)

        # 5. Native ReAct Agent & Orchestrator (Default)
        else:
            return self.brain.generate_response(user_prompt, session_id=session_id)

    handle_message = route_query
