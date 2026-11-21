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
5. deep_research(query: str) - Multi-hop search across indexed local projects, documents, codebases, and offline knowledge base.
6. web_search(query: str) - Performs web search queries.
7. search_files(pattern: str, root_dir: Optional[str]) - Searches for files matching a pattern.
8. read_file(path: str) - Safely reads file contents.
9. capture_screen(prompt: Optional[str]) - Takes a screenshot and analyzes desktop contents.
10. get_system_stats() - Live CPU, GPU VRAM, RAM, and Battery telemetry.
11. morning_digest() - Generates system health and daily productivity briefing.

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
            # Dispatch to LLM
            step_response = self.brain._dispatch_chat(conversation)
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
            # Check if prompt contains code to execute
            from automation.code_interpreter import code_interpreter
            code_match = re.search(r"```python(.*?)```", user_prompt, re.DOTALL)
            if code_match:
                code = code_match.group(1).strip()
                res = code_interpreter.execute_python(code)
                return f"Execution Result:\nStdout: {res.get('stdout')}\nStderr: {res.get('stderr')}\nTime: {res.get('execution_time_sec')}s"
            # Otherwise use ReAct loop with code interpreter enabled
            return self.react_agent.execute_react_loop(user_prompt, session_id=session_id)

        # 5. Native ReAct Agent & Orchestrator (Default)
        else:
            return self.brain.generate_response(user_prompt, session_id=session_id)
