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
from automation.browser_controller import browser_controller
from vision.visual_analyzer import visual_analyzer


class UniversalAgentBrain:
    def __init__(self):
        self.user_title = config.get("system", "user_title", "Sir")
        self.primary_model = config.get("agent", "primary_model", "titan:latest")
        self._active_provider = "none"
        self._active_endpoint = ""
        self._query_cache: Dict[str, str] = {
            "who are you": "I am TITAN, your personal tactical desktop AI assistant running locally on your HP Victus hardware.",
            "what is your name": "My name is TITAN, Sir.",
            "what can you do": "I can execute A-to-Z automation: write and run code, browse the web and YouTube, open and close software, manage your files, adjust system controls, and monitor hardware.",
            "help": "You can speak or type commands to open software, write code in the Code Assistant, search YouTube, adjust volume, inspect projects, or run deep research queries.",
        }
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

            elif tool_name == "close_application":
                app_name = args.get("app_name", "")
                return app_controller.close_app(app_name)

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

            elif tool_name == "browser_action":
                act = args.get("action", "youtube_search")
                tgt = args.get("target", "")
                extra = args.get("extra", None)
                # Normalize target if model passed full URL
                if "youtube.com/" in tgt:
                    tgt = tgt.rstrip("/").split("/")[-1].replace("@", "").replace("user/", "")
                if act in ("youtube_search", "subscribe", "youtube") or "youtube" in tgt.lower() or "channel" in tgt.lower() or "subscribe" in str(extra).lower():
                    should_sub = args.get("subscribe", True) or "subscribe" in str(extra).lower()
                    emoji = extra if extra and any(e in extra for e in ("😊", "smile", "emoji")) else None
                    return browser_controller.execute_youtube_action(
                        tgt,
                        subscribe=should_sub,
                        find_live=args.get("find_live", True),
                        comment_or_emoji=emoji
                    )
                elif act == "open_url":
                    return browser_controller.open_url(tgt)
                return browser_controller.navigate_and_interact(tgt)

            elif tool_name == "deep_web_research":
                q = args.get("query", "")
                limit = int(args.get("max_sites", 3))
                return browser_controller.deep_web_research(q, max_sites=limit)

            elif tool_name == "execute_python":
                from automation.code_interpreter import code_interpreter
                code = args.get("code", "")
                return code_interpreter.execute_python(code)

            elif tool_name == "deep_research":
                from automation.deep_research import deep_research
                q = args.get("query", "")
                return deep_research.deep_research_query(q)

            elif tool_name == "morning_digest":
                from automation.daily_briefing import daily_briefing
                return daily_briefing.generate_morning_digest()

            elif tool_name == "write_file":
                p = args.get("path", "")
                c = args.get("content", "")
                ow = args.get("overwrite", True)
                return file_manager.write_file(p, c, overwrite=ow)

            elif tool_name == "list_directory":
                dp = args.get("dir_path", ".")
                return file_manager.list_directory(dp)

            elif tool_name == "execute_shell":
                from automation.code_interpreter import code_interpreter
                cmd = args.get("command", "")
                return code_interpreter.execute_shell(cmd)

            elif tool_name == "gui_click":
                from automation.gui_controller import gui_controller
                return gui_controller.click(
                    x=args.get("x"),
                    y=args.get("y"),
                    button=args.get("button", "left"),
                    double=args.get("double", False)
                )

            elif tool_name == "gui_type":
                from automation.gui_controller import gui_controller
                return gui_controller.type_text(args.get("text", ""))

            elif tool_name == "gui_hotkey":
                from automation.gui_controller import gui_controller
                return gui_controller.send_hotkey(args.get("keys", []))

            elif tool_name == "set_brightness":
                return system_control.set_brightness(args.get("level", 50))

            elif tool_name == "empty_recycle_bin":
                return system_control.empty_recycle_bin()

            elif tool_name == "arrange_workspace":
                left = args.get("left_app", "code")
                right = args.get("right_app", "chrome")
                return app_controller.arrange_workspace_windows(left, right)

            elif tool_name == "execute_routine":
                from automation.routines import routines
                return routines.execute_routine(args.get("routine_name", "dev_session"))

            elif tool_name == "morning_briefing":
                from automation.watchdog import watchdog
                return {"success": True, "briefing": watchdog.generate_morning_briefing()}

            elif tool_name == "analyze_document":
                from automation.document_intelligence import doc_intelligence
                p = args.get("file_path", "")
                q = args.get("question")
                return doc_intelligence.analyze_document(p, q)

            elif tool_name == "debug_screen":
                from vision.screen_sense import screen_sense
                return screen_sense.debug_screen(args.get("hint"))

            elif tool_name == "create_new_skill":
                from automation.skill_creator import skill_creator
                return skill_creator.create_skill(args.get("skill_name", ""), args.get("requirement", ""))

            elif tool_name == "manage_tasks":
                from core.task_board import task_board
                act = args.get("action", "list").lower()
                if act == "add":
                    return task_board.add_task(args.get("title", "Task"), args.get("description", ""), args.get("priority", "normal"))
                elif act in ("update", "complete", "done"):
                    return task_board.update_status(int(args.get("task_id", 1)), args.get("status", "done"))
                elif act == "delete":
                    return task_board.delete_task(int(args.get("task_id", 1)))
                else:
                    return {"success": True, "tasks": task_board.list_tasks(args.get("status")), "summary": task_board.get_summary()}

            elif tool_name == "web_download":
                from automation.web_agent import web_agent
                return web_agent.download_file(args.get("url", ""), args.get("filename"))

            elif tool_name == "extract_web_data":
                from automation.web_agent import web_agent
                return web_agent.scrape_web_tables_and_links(args.get("url", ""))

            elif tool_name == "generate_code":
                from automation.coding_agent import CodingAgent
                coder = CodingAgent(self)
                req = args.get("requirement") or args.get("prompt") or args.get("description", "")
                return {"success": True, "message": coder.generate_and_deliver_code(req, session_id="main")}

            else:
                from automation.skill_creator import skill_creator
                if tool_name in skill_creator.loaded_skills:
                    return skill_creator.execute_custom_skill(tool_name, args)
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

    def chat(self, prompt: str, session_id: str = "main") -> str:
        """Convenience alias for generate_response."""
        return self.generate_response(prompt, session_id=session_id)

    def generate_response(self, user_prompt: str, session_id: str = "main", on_chunk: Optional[Callable[[str], None]] = None) -> str:
        self._detect_provider()

        # Direct intent intercept for browser, youtube, and media automation
        prompt_lower = user_prompt.lower().strip()

        # Instant 1ms LRU query cache for deterministic questions
        cache_key = prompt_lower.rstrip("?.!")
        if cache_key in self._query_cache:
            reply = self._query_cache[cache_key]
            memory.add_message(session_id, "user", user_prompt)
            memory.add_message(session_id, "assistant", reply)
            if on_chunk:
                on_chunk(reply)
            return reply

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
                try:
                    final_reply = self._dispatch_chat(messages)
                    if not final_reply or HermesToolParser.parse_tool_call(final_reply):
                        final_reply = tool_result.get("message") or f"Operation '{tool_name}' completed successfully, Sir."
                except Exception:
                    final_reply = tool_result.get("message") or f"Operation '{tool_name}' completed successfully, Sir."
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

    def _dispatch_chat(self, messages: List[Dict[str, str]], on_chunk: Optional[Callable[[str], None]] = None) -> str:
        if self._active_provider == "ollama":
            endpoint = f"{self._active_endpoint}/api/chat"
            use_stream = bool(on_chunk)
            payload = {
                "model": self.primary_model,
                "messages": messages,
                "stream": use_stream,
                "keep_alive": -1,
                "options": {
                    "temperature": config.get("agent", "temperature", 0.2),
                    "num_ctx": config.get("agent", "num_ctx", 4096),
                    "num_thread": config.get("agent", "num_thread", 6),
                    "num_gpu": 99,
                    "f16_kv": True
                }
            }
        else:
            # OpenAI compatible endpoint (Msty, LM Studio, etc.)
            endpoint = f"{self._active_endpoint}/chat/completions"
            use_stream = False
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

        if use_stream and self._active_provider == "ollama":
            full_text = []
            with urllib.request.urlopen(req, timeout=180) as resp:
                for line in resp:
                    if line:
                        try:
                            chunk = json.loads(line.decode("utf-8"))
                            piece = chunk.get("message", {}).get("content", "")
                            if piece:
                                full_text.append(piece)
                                if on_chunk:
                                    on_chunk(piece)
                        except Exception:
                            continue
            return "".join(full_text)
        else:
            with urllib.request.urlopen(req, timeout=180) as resp:
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
        elif any(w in lower for w in ("youtube", "open chrome", "browse", "navigate")):
            from automation.browser_controller import browser_controller
            target = ""
            for marker in ("search for", "search", "navigate to", "channel", "open"):
                if marker in lower:
                    parts = lower.split(marker)
                    if len(parts) > 1 and parts[-1].strip():
                        target = parts[-1].strip().replace("channel", "").strip()
                        break
            res = browser_controller.execute_youtube_action(target or "trending")
            return res.get("message", f"Navigated to YouTube for '{target or 'trending'}', Sir.")

        return (
            f"Good day, {self.user_title}. All local AI runtimes (Ollama, Msty Studio, LM Studio) are currently offline. "
            f"Please launch your model engine (e.g. run 'ollama serve' or open Msty Studio) to activate full conversational reasoning."
        )


brain = UniversalAgentBrain()
