"""
Universal JARVIS Agent Brain.
Supports Nous Hermes function calling, Msty Studio, Ollama, LM Studio, and OpenAI-compatible local/cloud APIs.
Includes dynamic provider detection, tool execution, and context memory.
"""

import json
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, List, Optional, Tuple
from config.config_manager import config
from core.memory import memory
from core.telemetry import telemetry
from core.hermes_parser import HermesToolParser, HERMES_SYSTEM_PROMPT
from automation.permissions import permissions
from automation.app_controller import app_controller
from automation.file_manager import file_manager
from automation.system_control import system_control
from automation.web_researcher import web_researcher
from vision.visual_analyzer import visual_analyzer


class UniversalAgentBrain:
    def __init__(self):
        self.user_title = config.get("system", "user_title", "Sir")
        self.primary_model = config.get("agent", "primary_model", "hermes3:8b")
        self._active_provider = "none"
        self._active_endpoint = ""
        self._detect_provider()

    def _detect_provider(self) -> Tuple[str, str]:
        """
        Probe available local and configured endpoints in order:
        1. Ollama (native & /v1)
        2. Msty Studio Local API (/v1)
        3. LM Studio (/v1)
        """
        endpoints = config.get("agent", "endpoints", {})
        
        # Check Ollama
        ollama_url = endpoints.get("ollama", "http://127.0.0.1:11434")
        if self._ping_url(f"{ollama_url}/api/tags"):
            self._active_provider = "ollama"
            self._active_endpoint = ollama_url
            return self._active_provider, self._active_endpoint

        # Check Msty Studio local API
        msty_url = endpoints.get("msty", "http://127.0.0.1:1024/v1")
        if self._ping_url(f"{msty_url}/models"):
            self._active_provider = "msty"
            self._active_endpoint = msty_url
            return self._active_provider, self._active_endpoint

        # Check LM Studio
        lm_url = endpoints.get("lmstudio", "http://127.0.0.1:1234/v1")
        if self._ping_url(f"{lm_url}/models"):
            self._active_provider = "lmstudio"
            self._active_endpoint = lm_url
            return self._active_provider, self._active_endpoint

        self._active_provider = "offline"
        self._active_endpoint = ""
        return self._active_provider, self._active_endpoint

    def _ping_url(self, url: str) -> bool:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "JARVIS-Agent/1.0"})
            with urllib.request.urlopen(req, timeout=1.2) as resp:
                return resp.status in (200, 204)
        except Exception:
            return False

    @property
    def status(self) -> Dict[str, Any]:
        self._detect_provider()
        return {
            "provider": self._active_provider,
            "endpoint": self._active_endpoint,
            "model": self.primary_model,
            "is_online": self._active_provider != "offline"
        }

    def is_ollama_online(self) -> bool:
        self._detect_provider()
        return self._active_provider == "ollama"

    def list_local_models(self) -> List[str]:
        return self.list_models()
        self._detect_provider()
        if self._active_provider == "ollama":
            try:
                req = urllib.request.Request(f"{self._active_endpoint}/api/tags")
                with urllib.request.urlopen(req, timeout=2) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return [m["name"] for m in data.get("models", [])]
            except Exception:
                return []
        elif self._active_provider in ("msty", "lmstudio"):
            try:
                req = urllib.request.Request(f"{self._active_endpoint}/models")
                with urllib.request.urlopen(req, timeout=2) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return [m["id"] for m in data.get("data", [])]
            except Exception:
                return []
        return []

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a local automation tool safely through permissions gate."""
        if not permissions.is_permitted(tool_name, args):
            return {"error": f"Permission denied for tool '{tool_name}' under current security profile."}

        try:
            if tool_name == "get_system_stats":
                return telemetry.get_full_telemetry()

            elif tool_name == "open_application":
                app_name = args.get("app_name", "")
                extra_args = args.get("args", [])
                return app_controller.launch_app(app_name, extra_args)

            elif tool_name == "find_projects":
                root = args.get("root_dir")
                return {"projects": file_manager.find_projects(root)}

            elif tool_name == "search_files":
                pattern = args.get("pattern", "")
                root = args.get("root_dir")
                return {"matches": file_manager.search_files(pattern, root)}

            elif tool_name == "read_file":
                path = args.get("path", "")
                return file_manager.read_file(path)

            elif tool_name == "inspect_project":
                path = args.get("path", "")
                return file_manager.inspect_directory_tree(path)

            elif tool_name == "capture_screen":
                prompt = args.get("prompt", "Analyze what is visible on screen.")
                return visual_analyzer.analyze_screen(prompt)

            elif tool_name == "web_search":
                query = args.get("query", "")
                return {"results": web_researcher.search(query)}

            elif tool_name == "lock_workstation":
                return system_control.lock_workstation()

            elif tool_name == "volume_control":
                action = args.get("action", "up")
                if action == "mute":
                    return system_control.volume_mute()
                elif action == "down":
                    return system_control.volume_down()
                return system_control.volume_up()

            else:
                return {"error": f"Unknown tool: '{tool_name}'"}
        except Exception as e:
            return {"error": f"Tool execution failed: {e}"}

    def _build_hermes_prompt(self) -> str:
        t = telemetry.get_full_telemetry()
        vram_mb = t["gpu"]["vram_used_mb"]
        cpu_pct = t["cpu"]["percent"]
        ram_pct = t["ram"]["percent"]
        battery = t["battery"]["percent"]

        tools_schema = HermesToolParser.get_hermes_tools_prompt()

        system_prompt = f"""{HERMES_SYSTEM_PROMPT}

Live System Telemetry:
- Hardware: {t['gpu']['name']} (VRAM Used: {vram_mb} / 4096 MB)
- CPU Utilization: {cpu_pct}% | Memory: {ram_pct}% | Battery: {battery}%
- Active Agent Provider: {self._active_provider.upper()} ({self.primary_model})

{tools_schema}
"""
        return system_prompt

    def generate_response(self, user_prompt: str, session_id: str = "main", on_chunk: Optional[Callable[[str], None]] = None) -> str:
        self._detect_provider()

        # Handle offline fallback with smart heuristics
        if self._active_provider == "offline":
            return self._handle_offline_intent(user_prompt)

        # Retrieve recent history from memory
        history = memory.get_recent_messages(session_id, limit=6)
        messages = [{"role": "system", "content": self._build_hermes_prompt()}]
        for m in history:
            messages.append({"role": m["role"], "content": m["content"]})
        messages.append({"role": "user", "content": user_prompt})

        memory.add_message(session_id, "user", user_prompt)

        # Call active engine
        try:
            reply = self._dispatch_chat(messages)

            # Check if model invoked a tool using Hermes format or JSON block
            tool_call = HermesToolParser.parse_tool_call(reply)
            if tool_call:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("arguments", {})

                # Execute tool
                tool_result = self.execute_tool(tool_name, tool_args)

                # Feed result back using Hermes <tool_response> standard
                messages.append({"role": "assistant", "content": reply})
                messages.append({
                    "role": "user",
                    "content": HermesToolParser.format_tool_response(tool_name, tool_result)
                })

                # Second turn: synthesize response
                final_reply = self._dispatch_chat(messages)
                memory.add_message(session_id, "assistant", final_reply)
                if on_chunk:
                    on_chunk(final_reply)
                return final_reply

            memory.add_message(session_id, "assistant", reply)
            if on_chunk:
                on_chunk(reply)
            return reply

        except Exception as e:
            err_msg = f"My apologies, {self.user_title}. An error occurred communicating with the {self._active_provider} engine: {e}"
            memory.add_message(session_id, "assistant", err_msg)
            return err_msg

    def _dispatch_chat(self, messages: List[Dict[str, str]]) -> str:
        if self._active_provider == "ollama":
            endpoint = f"{self._active_endpoint}/api/chat"
            payload = {
                "model": self.primary_model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": config.get("agent", "temperature", 0.2)}
            }
        else:
            # OpenAI compatible endpoint (Msty, LM Studio, etc.)
            endpoint = f"{self._active_endpoint}/chat/completions"
            payload = {
                "model": self.primary_model,
                "messages": messages,
                "temperature": config.get("agent", "temperature", 0.2),
                "stream": False
            }

        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=35) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if self._active_provider == "ollama":
                return data.get("message", {}).get("content", "")
            else:
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    def _handle_offline_intent(self, text: str) -> str:
        lower = text.lower().strip()
        if any(w in lower for w in ["status", "telemetry", "hardware", "specs"]):
            t = telemetry.get_full_telemetry()
            return f"Offline telemetry: CPU {t['cpu']['percent']}%, RAM {t['ram']['percent']}%, GPU {t['gpu']['name']} at {t['gpu']['temperature_c']}°C. Local AI runtime is currently offline."
        elif "open vs code" in lower or "open code" in lower:
            app_controller.launch_app("vscode")
            return f"Opening Visual Studio Code for you, {self.user_title}."
        elif "lock" in lower and ("pc" in lower or "computer" in lower or "system" in lower):
            system_control.lock_workstation()
            return f"Locking workstation now, {self.user_title}."

        return (
            f"Good day, {self.user_title}. All local AI runtimes (Ollama, Msty Studio, LM Studio) are currently offline. "
            f"Please launch your model engine (e.g. run 'ollama serve' or open Msty Studio) to activate full conversational reasoning."
        )


brain = UniversalAgentBrain()
