# J.A.R.V.I.S. – Personal Desktop AI Assistant 🤖

[![GitHub Repository](https://img.shields.io/badge/GitHub-vishwajith2402%2FJARVIS-blue?logo=github)](https://github.com/vishwajith2402/JARVIS)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-green)](https://www.python.org/)
[![Hardware Target](https://img.shields.io/badge/Hardware-HP%20Victus%20%7C%20RTX%203050-orange)](https://nvidia.com)

**J.A.R.V.I.S. (Just A Rather Versatile Intelligent System)** is a local, privacy-first personal AI assistant built for Windows. It features a tactical desktop HUD interface, background wake-word voice interaction, screen comprehension, hardware telemetry, and Windows computer automation.

Optimized specifically for the **HP Victus 15** (AMD Ryzen 5, NVIDIA RTX 3050 4GB VRAM, 16GB RAM).

---

## 🌟 Key Architecture & Capabilities

1. **Dual Operating Modes**:
   - **Mode 1 (Desktop HUD Dashboard)**: Futuristic desktop application featuring holographic arc reactor visualizer, real-time hardware telemetry gauges (RTX 3050 VRAM, CPU, RAM, battery), streaming chat, and tactical direct actions.
   - **Mode 2 (Background Voice Daemon)**: Runs quietly in background, activating via wake word (*"Hey Jarvis"*) or hotkey (`Ctrl+Shift+J`), executing commands, and speaking responses aloud.

2. **Universal AI Agent Brain & Vision**:
   - Upgraded to support **Nous Hermes 3 Agent** (`hermes3:8b`), **Msty Studio Local API**, and **Ollama**.
   - Implements native Hermes `<tool_call>` function calling and XML/JSON tool extraction with zero hallucination.
   - Dynamic provider auto-detection: checks Ollama, Msty Studio, and LM Studio automatically.
   - Screen vision analysis powered by `moondream`.

3. **Multi-Tier Security & Automation**:
   - **Level 1 (Automatic)**: Safe read-only telemetry, file searching, project indexing.
   - **Level 2 (Confirmation)**: Launching applications, creating files, visual screen grabs.
   - **Level 3 (Restricted)**: Destructive file operations, killing processes, shell execution.

4. **Speech & Audio**:
   - Zero-latency Windows SAPI speech synthesizer with British/English cadence.
   - Speech-to-text recognition with noise calibration.

5. **Persistent SQLite Memory**:
   - Contextual conversation history, project registry, task tracker, and remembered facts.

---

## 📁 Repository Structure

```
D:\Practice Projects\JARVIS\
├── config/
│   ├── settings.json          # Core settings (models, voice, permissions, paths)
│   └── config_manager.py      # Thread-safe configuration manager
├── core/
│   ├── brain.py               # Ollama LLM client, tool execution, persona
│   ├── memory.py              # SQLite persistent database
│   ├── planner.py             # Multi-step task planner
│   └── telemetry.py           # Real-time RTX 3050 & system telemetry
├── voice/
│   ├── speaker.py             # Windows SAPI voice synthesizer
│   ├── listener.py            # Speech recognition & mic capture
│   └── wake_word.py           # Wake-word ("Hey Jarvis") detector
├── vision/
│   ├── screen_capture.py      # Fullscreen & window capture
│   └── visual_analyzer.py     # Vision model client (Moondream)
├── automation/
│   ├── permissions.py         # 3-tier security gate
│   ├── app_controller.py      # Windows application launcher & window focus
│   ├── file_manager.py        # Safe file & project tree manager
│   ├── system_control.py      # Volume, lock screen, system controls
│   └── web_researcher.py      # Free DuckDuckGo search integration
├── ui/
│   ├── hud_app.py             # Native desktop HUD window via pywebview
│   ├── tray.py                # Background daemon & wake listener
│   └── static/                # Holographic HUD frontend (HTML/CSS/JS Canvas)
├── tests/
│   └── test_components.py     # Unit test suite
├── main.py                    # Unified CLI & GUI launcher
├── requirements.txt           # Dependencies
└── INSTALLATION_GUIDE.md      # Detailed setup manual
```

---

## 🚀 Quick Start

### 1. Run Hardware Diagnostics
```powershell
python main.py --check
```

### 2. Launch Desktop HUD (Mode 1)
```powershell
python main.py
```

### 3. Launch Background Voice Assistant (Mode 2)
```powershell
python main.py --mode background
```

Refer to [INSTALLATION_GUIDE.md](file:///D:/Practice%20Projects/JARVIS/INSTALLATION_GUIDE.md) for complete instructions on installing Ollama, downloading `llama3.2:3b`, and setting up Msty Studio.
