"""
SQLite Memory System for JARVIS.
Stores conversations, user preferences, projects, tasks, and knowledge facts.
"""

import json
import sqlite3
import time
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

def _resolve_db_path() -> Path:
    candidates = [
        DATA_DIR / "jarvis_memory.db",
        Path.home() / ".titan" / "jarvis_memory.db",
        Path(tempfile.gettempdir()) / "titan_memory.db"
    ]
    for c in candidates:
        try:
            c.parent.mkdir(parents=True, exist_ok=True)
            test_conn = sqlite3.connect(c)
            test_conn.execute("CREATE TABLE IF NOT EXISTS _write_probe (x INT)")
            test_conn.execute("INSERT INTO _write_probe VALUES (1)")
            test_conn.execute("DELETE FROM _write_probe")
            test_conn.commit()
            test_conn.close()
            return c
        except Exception:
            continue
    return Path(":memory:")

DB_PATH = _resolve_db_path()


class MemoryManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if hasattr(self, "_fallback_memory") and self._fallback_memory:
            return self._memory_conn

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            # Test write ability
            conn.execute("CREATE TABLE IF NOT EXISTS _test (id INT)")
            return conn
        except sqlite3.OperationalError:
            self._fallback_memory = True
            self._memory_conn = sqlite3.connect(":memory:")
            self._memory_conn.row_factory = sqlite3.Row
            return self._memory_conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Conversation history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    intent TEXT DEFAULT 'general'
                )
            """)

            # User preferences and attributes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)

            # Tracked user projects
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    path TEXT NOT NULL,
                    language TEXT DEFAULT 'unknown',
                    last_accessed REAL NOT NULL,
                    notes TEXT DEFAULT ''
                )
            """)

            # Tasks and subtasks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at REAL NOT NULL,
                    completed_at REAL,
                    details TEXT DEFAULT ''
                )
            """)

            # General knowledge / remembered facts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    fact TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
            """)

            conn.commit()

    # --- Conversation Operations ---
    def add_message(self, session_id: str, role: str, content: str, intent: str = "general") -> None:
        with self._get_connection() as conn:
            conn.cursor().execute(
                "INSERT INTO conversations (session_id, timestamp, role, content, intent) VALUES (?, ?, ?, ?, ?)",
                (session_id, time.time(), role, content, intent)
            )
            conn.commit()

    def get_recent_messages(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content, intent, timestamp FROM conversations WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit)
            )
            rows = cursor.fetchall()
            return [dict(r) for r in reversed(rows)]

    def clear_session(self, session_id: str) -> None:
        with self._get_connection() as conn:
            conn.cursor().execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
            conn.commit()

    # --- Preferences Operations ---
    def set_preference(self, key: str, value: Any) -> None:
        val_str = json.dumps(value) if not isinstance(value, str) else value
        with self._get_connection() as conn:
            conn.cursor().execute(
                "INSERT INTO preferences (key, value, updated_at) VALUES (?, ?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                (key, val_str, time.time())
            )
            conn.commit()

    def get_preference(self, key: str, default: Any = None) -> Any:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row["value"])
                except Exception:
                    return row["value"]
            return default

    # --- Project Management Operations ---
    def register_or_update_project(self, name: str, path: str, language: str = "unknown", notes: str = "") -> None:
        with self._get_connection() as conn:
            conn.cursor().execute(
                """
                INSERT INTO projects (name, path, language, last_accessed, notes)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    path=excluded.path,
                    language=excluded.language,
                    last_accessed=excluded.last_accessed,
                    notes=excluded.notes
                """,
                (name, path, language, time.time(), notes)
            )
            conn.commit()

    def get_project(self, name: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE name LIKE ?", (f"%{name}%",))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_projects(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects ORDER BY last_accessed DESC")
            return [dict(r) for r in cursor.fetchall()]

    # --- Tasks Operations ---
    def add_task(self, title: str, details: str = "") -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tasks (title, status, created_at, details) VALUES (?, 'pending', ?, ?)",
                (title, time.time(), details)
            )
            conn.commit()
            return cursor.lastrowid

    def update_task_status(self, task_id: int, status: str) -> None:
        completed_at = time.time() if status in ("completed", "done") else None
        with self._get_connection() as conn:
            conn.cursor().execute(
                "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
                (status, completed_at, task_id)
            )
            conn.commit()

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE status != 'completed' ORDER BY id DESC")
            return [dict(r) for r in cursor.fetchall()]

    # --- Facts / Long-term Memory ---
    def remember_fact(self, category: str, subject: str, fact: str) -> None:
        with self._get_connection() as conn:
            conn.cursor().execute(
                "INSERT INTO facts (category, subject, fact, created_at) VALUES (?, ?, ?, ?)",
                (category, subject, fact, time.time())
            )
            conn.commit()

    def search_facts(self, query: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            pattern = f"%{query}%"
            cursor.execute(
                "SELECT * FROM facts WHERE subject LIKE ? OR fact LIKE ? ORDER BY id DESC LIMIT 5",
                (pattern, pattern)
            )
            return [dict(r) for r in cursor.fetchall()]


memory = MemoryManager()
