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
                "name": "arrange_workspace",
                "description": "Auto-tile and arrange open software side-by-side (e.g. VS Code on the left half, Chrome on the right half).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "left_app": {"type": "string", "description": "Software to tile on the left half of the display."},
                        "right_app": {"type": "string", "description": "Software to tile on the right half of the display."}
                    }
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
        },
        {
            "type": "function",
            "function": {
                "name": "generate_code",
                "description": "Generate complete, functional, immediately executable Python or Web software (apps, GUI, Tkinter, games, tools, calculators) and save to sandbox.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "requirement": {"type": "string", "description": "The exact requirements or software to generate."}
                    },
                    "required": ["requirement"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write or create files with text or code on the filesystem.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Full path to file."},
                        "content": {"type": "string", "description": "Text or code to write."},
                        "overwrite": {"type": "boolean", "description": "Whether to overwrite if exists."}
                    },
                    "required": ["path", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_directory",
                "description": "List files and folders in any directory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dir_path": {"type": "string", "description": "Target folder path."}
                    },
                    "required": ["dir_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "execute_shell",
                "description": "Execute PowerShell or CMD commands in workspace (install packages, system queries, etc.).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Command string to execute."}
                    },
                    "required": ["command"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "gui_click",
                "description": "Native Windows mouse click at (x, y) coordinates on screen.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "x": {"type": "integer", "description": "X coordinate."},
                        "y": {"type": "integer", "description": "Y coordinate."},
                        "button": {"type": "string", "enum": ["left", "right", "middle"], "description": "Mouse button."},
                        "double": {"type": "boolean", "description": "Whether double click."}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "gui_type",
                "description": "Type text directly into the focused window/application.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to type into window."}
                    },
                    "required": ["text"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "gui_hotkey",
                "description": "Send keyboard shortcut sequence (e.g. ['ctrl', 's'], ['alt', 'f4'], ['enter']).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keys": {"type": "array", "items": {"type": "string"}, "description": "List of key names."}
                    },
                    "required": ["keys"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "set_brightness",
                "description": "Adjust monitor brightness (0 to 100%).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "level": {"type": "integer", "description": "Brightness percentage."}
                    },
                    "required": ["level"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "empty_recycle_bin",
                "description": "Clean and empty the Windows Recycle Bin.",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "arrange_workspace",
                "description": "Tile two open application windows side-by-side (50% left, 50% right) on screen.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "left_app": {"type": "string", "description": "Name or executable of app for left side (e.g. 'code', 'notepad')."},
                        "right_app": {"type": "string", "description": "Name or executable of app for right side (e.g. 'chrome', 'edge')."}
                    },
                    "required": ["left_app", "right_app"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "deep_web_research",
                "description": "Perform deep multi-site web research, extract key content, and display synthesis.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The search query or research topic."},
                        "max_sites": {"type": "integer", "description": "Maximum number of sites to crawl and extract (default: 3)."}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "manage_profile",
                "description": "View or update executive user profile (name, title, preferred stacks, IDE, work style).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["get", "update"], "description": "Action type."},
                        "updates": {"type": "object", "description": "Dictionary of fields to update if action is update."}
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remember_fact",
                "description": "Store a permanent knowledge fact about the user, preference, project, or instruction.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "description": "Category (e.g. 'preference', 'tech', 'project', 'instruction')."},
                        "subject": {"type": "string", "description": "Topic or entity (e.g. 'database', 'frontend', 'schedule')."},
                        "fact": {"type": "string", "description": "The exact fact or rule to remember."}
                    },
                    "required": ["category", "subject", "fact"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "recall_facts",
                "description": "Search and retrieve stored knowledge facts and rules from long-term memory.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Optional search query to filter facts."}
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "plan_business_goal",
                "description": "Establish and hierarchically decompose a company strategic goal into departmental milestones (Engineering, Marketing, Sales, Operations).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "High-level strategic business objective or goal."},
                        "description": {"type": "string", "description": "Detailed business context and desired outcomes."},
                        "category": {"type": "string", "description": "Category (growth, revenue, product, branding)."}
                    },
                    "required": ["title", "description"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_invoice",
                "description": "Generate a professional client invoice in clean responsive HTML and save to disk.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "client_name": {"type": "string", "description": "Client company or person name."},
                        "client_email": {"type": "string", "description": "Client email address."},
                        "line_items": {"type": "array", "items": {"type": "object"}, "description": "List of items with description, quantity, and rate."},
                        "tax_pct": {"type": "number", "description": "Tax percentage (e.g. 0.0 or 10.0)."}
                    },
                    "required": ["client_name", "line_items"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "manage_leads",
                "description": "Add, list, or update B2B sales prospects and CRM deals.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["add", "list", "update"], "description": "Action to perform."},
                        "company": {"type": "string", "description": "Company name."},
                        "contact_name": {"type": "string", "description": "Contact person name."},
                        "estimated_value": {"type": "number", "description": "Deal value in USD."},
                        "status": {"type": "string", "description": "CRM status (new, contacted, qualified, proposal, won, lost)."}
                    },
                    "required": ["action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "craft_cold_outreach",
                "description": "Draft a personalized, high-converting B2B cold outreach email to a prospect.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "company": {"type": "string", "description": "Target prospect company name."},
                        "contact_name": {"type": "string", "description": "Prospect contact name."},
                        "pain_point": {"type": "string", "description": "Specific business or technical pain point to address."}
                    },
                    "required": ["company"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_business_summary",
                "description": "Retrieve comprehensive company health metrics (revenue, profit, CRM pipeline, OKR progress).",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_competitors",
                "description": "Produce a competitive analysis report, SWOT breakdown, and strategic positioning matrix.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "industry": {"type": "string", "description": "Industry niche or product category."},
                        "competitors": {"type": "array", "items": {"type": "string"}, "description": "List of competitor names."}
                    },
                    "required": ["industry"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_marketing_content",
                "description": "Generate high-converting marketing campaigns, blog posts, social threads, or press releases.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content_type": {"type": "string", "enum": ["blog_post", "social_thread", "product_announcement"], "description": "Type of marketing asset."},
                        "topic": {"type": "string", "description": "Topic or launch subject."},
                        "target_audience": {"type": "string", "description": "Target customer segment."}
                    },
                    "required": ["content_type", "topic"]
                }
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

        # 2. XML tag element format: <tool_name key="val" ... /> or <tool_name key="val">...</tool_name>
        xml_match = re.search(r'<([a-zA-Z0-9_]+)\s+([^>]+?)\s*(?:/>|>)', text)
        if xml_match:
            tag = xml_match.group(1).lower()
            if tag not in ("tools", "tool_call", "tool_response", "system", "user", "assistant", "think"):
                attr_str = xml_match.group(2)
                attrs = {}
                for k, v in re.findall(r'([a-zA-Z0-9_]+)=["\']([^"\']*)["\']', attr_str):
                    attrs[k] = v
                if attrs:
                    return {"name": tag, "arguments": attrs}

        # 3. Action: tool_name(...) format
        action_match = re.search(r'Action:\s*([a-zA-Z0-9_]+)\s*\((.*?)\)', text, re.DOTALL)
        if action_match:
            name = action_match.group(1).strip()
            arg_str = action_match.group(2).strip()
            if not arg_str:
                return {"name": name, "arguments": {}}
            try:
                return {"name": name, "arguments": json.loads(arg_str)}
            except Exception:
                attrs = {}
                for k, v in re.findall(r'([a-zA-Z0-9_]+)\s*=\s*["\']([^"\']*)["\']', arg_str):
                    attrs[k] = v
                if attrs:
                    return {"name": name, "arguments": attrs}

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

        # 6. Plain text invocation: tool_name { ... } or tool_name({...})
        plain_match = re.search(r'\b([a-zA-Z0-9_]{3,30})\s*(?:(?:\(|\s*)\s*(\{[\s\S]*?\})\s*\)?)', text)
        if plain_match:
            cand_name = plain_match.group(1).strip()
            raw_json = plain_match.group(2)
            try:
                call_args = json.loads(raw_json)
                if isinstance(call_args, dict):
                    return {"name": cand_name, "arguments": call_args}
            except Exception:
                try:
                    call_args = json.loads(cls._clean_json_str(raw_json))
                    if isinstance(call_args, dict):
                        return {"name": cand_name, "arguments": call_args}
                except Exception:
                    pass

        return None

    @classmethod
    def format_tool_response(cls, tool_name: str, result: Dict[str, Any]) -> str:
        """Format tool result using Hermes standard <tool_response> tags."""
        result_json = json.dumps(result, indent=2)
        return f"<tool_response>\n{{\"name\": \"{tool_name}\", \"content\": {result_json}}}\n</tool_response>"
