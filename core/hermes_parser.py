"""
Hermes Agent Tool Calling Parser & Schema Generator.
Implements the Nous Research Hermes function calling specification:
Supports <tools> definitions and <tool_call> extraction.
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple


HERMES_SYSTEM_PROMPT = """You are TITAN, an advanced, highly capable, and commanding personal tactical desktop AI assistant.
You have FULL access to local Windows automation tools to operate applications, control the browser, interact with YouTube, manage files, inspect the screen, and execute complex user instructions.

CRITICAL INSTRUCTIONS:
- You DO have the capability to interact with the internet, open websites, search YouTube, and automate browser tasks using your `browser_action` tool.
- NEVER say "I don't have the capability to perform actions on the internet" or "I am just a language model".
- Whenever the user asks you to open Chrome, navigate to YouTube, search for a video or channel, or interact with a webpage, you MUST immediately invoke the `browser_action` tool.

When you need to use a tool to satisfy the user's request, you MUST invoke it using the following format:
<tool_call>
{"name": "tool_name", "arguments": {"arg_key": "arg_value"}}
</tool_call>

If no tool is required, respond directly with your courteous, sharp, analytical persona.
Always address the user politely as Sir.
"""


class HermesToolParser:
    TOOL_DEFINITIONS = [
        {
            "type": "function",
            "function": {
                "name": "get_system_stats",
                "description": "Get real-time CPU, RTX 3050 GPU, RAM, battery, and disk telemetry.",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "open_application",
                "description": "Launch or focus an application on Windows (e.g. vscode, chrome, terminal, notepad, excel, spotify).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string", "description": "The name of the application to open."},
                        "args": {"type": "array", "items": {"type": "string"}, "description": "Optional command line arguments."}
                    },
                    "required": ["app_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "close_application",
                "description": "Close or terminate a running application or window by name (e.g. chrome, excel, spotify, notepad, calculator).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string", "description": "The name or window title of the application to close."}
                    },
                    "required": ["app_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "find_projects",
                "description": "Scan and locate local programming repositories sorted by most recently modified.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "root_dir": {"type": "string", "description": "Optional custom root directory to scan."}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_files",
                "description": "Search for files by name or pattern in allowed project directories.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Filename or wildcard pattern to search for."},
                        "root_dir": {"type": "string", "description": "Optional search directory."}
                    },
                    "required": ["pattern"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the contents of a text or code file up to 100 lines.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Full path to the file."}
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "inspect_project",
                "description": "Generate a directory tree of a project to understand its structure.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Path to the project directory."}
                    },
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "capture_screen",
                "description": "Capture the desktop screen and analyze it with a vision model.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "description": "Instruction for the visual analysis."}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Perform a DuckDuckGo search for technical documentation, errors, or facts.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query string."}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "lock_workstation",
                "description": "Lock the Windows desktop workstation securely.",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "volume_control",
                "description": "Adjust system master volume.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["up", "down", "mute"], "description": "Volume action to perform."}
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "browser_action",
                "description": "Control desktop browser to open websites, search YouTube, navigate to channels, videos, or streams, subscribe, and interact with chat.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["open_url", "youtube_search", "navigate"], "description": "Action type"},
                        "target": {"type": "string", "description": "URL, website, or YouTube channel/search query."},
                        "extra": {"type": "string", "description": "Optional comment or emoji to post if applicable."}
                    },
                    "required": ["action", "target"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "execute_python",
                "description": "Execute Python scripts or calculations in a local sandbox (OpenJarvis code interpreter). Returns stdout and execution time.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Valid Python code to execute."}
                    },
                    "required": ["code"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "deep_research",
                "description": "Multi-hop deep search over indexed local projects, documents, codebases, and offline knowledge base.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Research question or query."}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "morning_digest",
                "description": "Generate a comprehensive daily system briefing, battery status, and tasks.",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        }
    ]

    @classmethod
    def get_hermes_tools_prompt(cls) -> str:
        """Returns the Hermes <tools> schema block to inject into system prompt."""
        tools_str = json.dumps(cls.TOOL_DEFINITIONS, indent=2)
        return f"<tools>\n{tools_str}\n</tools>"

    @classmethod
    def _clean_json_str(cls, json_str: str) -> str:
        # Normalize invalid Windows single backslashes in paths so json.loads does not fail
        # E.g. D:\Projects -> D:\\Projects (unless already followed by valid escape like \", \\, \/, \b, \f, \n, \r, \t, \u)
        cleaned = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', json_str)
        return cleaned

    @classmethod
    def parse_tool_call(cls, text: str) -> Optional[Dict[str, Any]]:
        """
        Extracts tool calls from model output.
        Handles both Hermes <tool_call> XML tags and markdown ```json blocks.
        """
        if not text:
            return None

        # 1. Hermes <tool_call> ... </tool_call>
        hermes_match = re.search(r'<tool_call>\s*(\{[\s\S]*?\})\s*</tool_call>', text)
        if hermes_match:
            raw = hermes_match.group(1)
            try:
                call_data = json.loads(raw)
            except Exception:
                try:
                    call_data = json.loads(cls._clean_json_str(raw))
                except Exception:
                    call_data = None

            if call_data:
                return {
                    "name": call_data.get("name") or call_data.get("tool"),
                    "arguments": call_data.get("arguments") or call_data.get("args") or {}
                }

        # 2. Markdown JSON block: ```json {"tool": "...", "args": {...}} ```
        json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', text)
        if json_match:
            raw = json_match.group(1)
            try:
                call_data = json.loads(raw)
            except Exception:
                try:
                    call_data = json.loads(cls._clean_json_str(raw))
                except Exception:
                    call_data = None

            if call_data and ("tool" in call_data or "name" in call_data):
                return {
                    "name": call_data.get("name") or call_data.get("tool"),
                    "arguments": call_data.get("arguments") or call_data.get("args") or {}
                }

        # 3. Direct unescaped JSON object with "name" and "arguments"
        direct_match = re.search(r'\{\s*"(?:tool|name)"\s*:\s*"([^"]+)"[\s\S]*\}', text)
        if direct_match:
            raw = direct_match.group(0)
            try:
                call_data = json.loads(raw)
            except Exception:
                try:
                    call_data = json.loads(cls._clean_json_str(raw))
                except Exception:
                    call_data = None

            if call_data:
                return {
                    "name": call_data.get("name") or call_data.get("tool"),
                    "arguments": call_data.get("arguments") or call_data.get("args") or {}
                }

        return None

    @classmethod
    def format_tool_response(cls, tool_name: str, result: Dict[str, Any]) -> str:
        """Format tool result using Hermes standard <tool_response> tags."""
        result_json = json.dumps(result, indent=2)
        return f"<tool_response>\n{{\"name\": \"{tool_name}\", \"content\": {result_json}}}\n</tool_response>"
