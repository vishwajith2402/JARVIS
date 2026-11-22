# Python System Automation & Data Processing Master Guide

## Core Principles
1. Always use `pathlib.Path` for cross-platform, robust file path manipulation.
2. UTF-8 file reading and writing with `encoding="utf-8", errors="replace"`.
3. Use `subprocess.Popen` or `subprocess.run` with `timeout` and `capture_output=True` to prevent hanging processes.
4. Clean JSON and SQLite data handling.

## Template: Safe Subprocess Execution
```python
import subprocess
import sys

def run_command_safely(command_list, timeout_sec=30):
    try:
        res = subprocess.run(
            command_list,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_sec
        )
        return {"success": res.returncode == 0, "stdout": res.stdout.strip(), "stderr": res.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Command timed out after {timeout_sec}s."}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Template: Fast CSV & File Parsing
```python
import csv
import json
from pathlib import Path

def convert_csv_to_json(csv_path, json_path):
    p_csv = Path(csv_path)
    p_json = Path(json_path)
    with open(p_csv, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        data = list(reader)
    with open(p_json, mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return len(data)
```
