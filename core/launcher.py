"""
JARVIS Agent Auto-Launcher.
Automatically detects, starts, and verifies local AI engine (Ollama) before JARVIS boots.
Handles:
- Finding the Ollama CLI executable across all known Windows install paths
- Starting 'ollama serve' as a hidden background process
- Waiting for the API to become ready with live status feedback
- Selecting the best available downloaded model
- Msty Studio and LM Studio detection (OpenAI-compatible endpoints)
"""

import os
import shutil
import subprocess
import time
import urllib.request
import urllib.error
from typing import Callable, Dict, List, Optional, Any


# Known install paths for Ollama on Windows
OLLAMA_SEARCH_PATHS = [
    r"C:\Users\HP\AppData\Local\Programs\Ollama\ollama.exe",
    r"C:\Users\HP\AppData\Local\ollama\ollama.exe",
    r"C:\Program Files\Ollama\ollama.exe",
    "ollama",
    "ollama.exe",
]

# OpenAI-compatible endpoints (Msty Studio, LM Studio, etc.)
OPENAI_COMPAT_ENDPOINTS = [
    ("msty",     "http://127.0.0.1:1024/v1"),
    ("lmstudio", "http://127.0.0.1:1234/v1"),
    ("custom",   "http://127.0.0.1:8080/v1"),
]

OLLAMA_API = "http://127.0.0.1:11434"


class AgentLauncher:
    def __init__(self,
                 preferred_model: str = "titan:latest",
                 fallback_models: Optional[List[str]] = None,
                 on_status: Optional[Callable[[str], None]] = None):
        self.preferred_model = preferred_model
        self.fallback_models = fallback_models or ["titan:latest", "llama3.2:3b", "hermes3:8b", "phi3.5:latest"]
        self.on_status = on_status or print
        self._ollama_proc: Optional[subprocess.Popen] = None

    def _emit(self, msg: str) -> None:
        self.on_status(msg)

    def _find_ollama_exe(self) -> Optional[str]:
        """Locate the ollama CLI executable."""
        # Fastest: check system PATH first
        path_resolved = shutil.which("ollama")
        if path_resolved:
            return path_resolved

        # Try known absolute paths
        for candidate in OLLAMA_SEARCH_PATHS:
            if os.path.isabs(candidate) and os.path.isfile(candidate):
                return candidate

        # Walk AppData\Local for any ollama.exe
        appdata = os.environ.get("LOCALAPPDATA", "")
        if appdata:
            for root, dirs, files in os.walk(appdata):
                dirs[:] = [d for d in dirs if d.lower() not in
                            ("cache", "temp", "node_modules", "crashreportclient",
                             "crashdumps", "cef", "d3dscache")]
                for f in files:
                    if f.lower() == "ollama.exe":
                        return os.path.join(root, f)
        return None

    def _is_ollama_api_up(self) -> bool:
        try:
            req = urllib.request.Request(
                f"{OLLAMA_API}/api/tags",
                headers={"User-Agent": "TITAN/1.4"}
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _check_openai_endpoints(self) -> Optional[Dict[str, str]]:
        for name, url in OPENAI_COMPAT_ENDPOINTS:
            try:
                req = urllib.request.Request(
                    f"{url}/models",
                    headers={"User-Agent": "TITAN/1.4"}
                )
                with urllib.request.urlopen(req, timeout=1.2) as resp:
                    if resp.status == 200:
                        return {"provider": name, "url": url}
            except Exception:
                continue
        return None

    def _start_ollama_serve(self, exe_path: str) -> bool:
        try:
            self._emit(f"[Launcher] Starting Ollama with FlashAttention & VRAM keep-alive: {exe_path}")
            env = os.environ.copy()
            env["OLLAMA_FLASH_ATTENTION"] = "1"
            env["OLLAMA_NUM_PARALLEL"] = "1"
            env["OLLAMA_MAX_LOADED_MODELS"] = "1"
            env["OLLAMA_KEEP_ALIVE"] = "-1"
            self._ollama_proc = subprocess.Popen(
                [exe_path, "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True
        except Exception as e:
            self._emit(f"[Launcher] Error starting Ollama: {e}")
            return False

    def _wait_for_api(self, timeout_sec: int = 30) -> bool:
        self._emit("[Launcher] Waiting for Ollama API to become ready...")
        for i in range(timeout_sec):
            if self._is_ollama_api_up():
                self._emit(f"[Launcher] Ollama API ready in {i + 1}s.")
                return True
            time.sleep(1)
        self._emit("[Launcher] Timed out waiting for Ollama API.")
        return False

    def _get_local_models(self) -> List[str]:
        import json
        try:
            req = urllib.request.Request(
                f"{OLLAMA_API}/api/tags",
                headers={"User-Agent": "TITAN/1.4"}
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            return []

    def _select_model(self) -> Optional[str]:
        local = self._get_local_models()
        self._emit(f"[Launcher] Downloaded models: {local if local else 'none found'}")
        candidates = [self.preferred_model] + self.fallback_models
        for c in candidates:
            if c in local:
                return c
            base = c.split(":")[0]
            for m in local:
                if m.startswith(base):
                    return m
        return None

    def ensure_agent_running(self) -> Dict[str, Any]:
        """
        Call at JARVIS startup to auto-launch the AI engine.
        Returns: {"success", "provider", "endpoint", "model", "message"}
        """
        # Step A: Is Ollama already running?
        if self._is_ollama_api_up():
            model = self._select_model() or self.preferred_model
            msg = f"Ollama already active. Using model: {model}"
            self._emit(f"[Launcher] {msg}")
            return {"success": True, "provider": "ollama",
                    "endpoint": OLLAMA_API, "model": model, "message": msg}

        # Step B: Check Msty / LM Studio
        openai_ep = self._check_openai_endpoints()
        if openai_ep:
            msg = f"{openai_ep['provider'].title()} detected at {openai_ep['url']}"
            self._emit(f"[Launcher] {msg}")
            return {"success": True, "provider": openai_ep["provider"],
                    "endpoint": openai_ep["url"], "model": self.preferred_model,
                    "message": msg}

        # Step C: Find and launch Ollama
        self._emit("[Launcher] No active AI engine found. Locating Ollama...")
        exe = self._find_ollama_exe()
        if not exe:
            msg = ("Ollama not found. Please install from https://ollama.com/download/windows "
                   "or launch Msty Studio with Local API enabled.")
            self._emit(f"[Launcher] {msg}")
            return {"success": False, "provider": "none",
                    "endpoint": "", "model": "", "message": msg}

        self._emit(f"[Launcher] Found Ollama at: {exe}")
        if not self._start_ollama_serve(exe):
            return {"success": False, "provider": "none",
                    "endpoint": "", "model": "", "message": "Could not start Ollama process."}

        if not self._wait_for_api(timeout_sec=30):
            return {"success": False, "provider": "none",
                    "endpoint": "", "model": "",
                    "message": "Ollama started but API not responding in 30s."}

        model = self._select_model() or self.preferred_model
        msg = f"Ollama started automatically. Active model: {model}"
        self._emit(f"[Launcher] {msg}")
        return {"success": True, "provider": "ollama",
                "endpoint": OLLAMA_API, "model": model, "message": msg}

    def shutdown_agent(self) -> None:
        """Cleanly terminate the Ollama process we spawned (if any)."""
        if self._ollama_proc:
            try:
                self._ollama_proc.terminate()
                self._emit("[Launcher] Ollama service stopped.")
            except Exception:
                pass
            self._ollama_proc = None


launcher = AgentLauncher()
