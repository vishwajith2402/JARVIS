"""
Interactive Task & Project Kanban Board for TITAN.
Persistently manages tasks and to-dos in SQLite (jarvis_memory.db).
Supports natural language task management via voice and text.
100% Free & Local.
"""

import sqlite3
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(r"D:\Practice Projects\JARVIS\data\jarvis_memory.db")
try:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
except Exception:
    pass


class TaskBoard:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_board (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    status TEXT DEFAULT 'todo',
                    priority TEXT DEFAULT 'normal',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def add_task(self, title: str, description: str = "", priority: str = "normal") -> Dict[str, Any]:
        """Add a new task to the board."""
        now = datetime.datetime.now().isoformat()
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO task_board (title, description, status, priority, created_at, updated_at)
                VALUES (?, ?, 'todo', ?, ?, ?)
            """, (title, description, priority, now, now))
            task_id = cur.lastrowid
            conn.commit()

        return {
            "success": True,
            "task_id": task_id,
            "title": title,
            "status": "todo",
            "message": f"Task #{task_id} ('{title}') added to your board, Sir."
        }

    def update_status(self, task_id: int, status: str) -> Dict[str, Any]:
        """Update task status ('todo', 'in_progress', 'done')."""
        valid_statuses = ("todo", "in_progress", "done")
        clean_status = status.lower().strip().replace(" ", "_")
        if clean_status not in valid_statuses:
            return {"success": False, "error": f"Invalid status: '{status}'. Choose from {valid_statuses}."}

        now = datetime.datetime.now().isoformat()
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE task_board
                SET status = ?, updated_at = ?
                WHERE id = ?
            """, (clean_status, now, int(task_id)))
            conn.commit()
            if cur.rowcount == 0:
                return {"success": False, "error": f"Task #{task_id} not found."}

        return {
            "success": True,
            "task_id": task_id,
            "new_status": clean_status,
            "message": f"Task #{task_id} marked as '{clean_status}', Sir."
        }

    def list_tasks(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tasks, optionally filtered by status."""
        query = "SELECT * FROM task_board"
        params = []
        if status_filter:
            query += " WHERE status = ?"
            params.append(status_filter.lower().strip())
        query += " ORDER BY id DESC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def delete_task(self, task_id: int) -> Dict[str, Any]:
        """Delete a task by ID."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM task_board WHERE id = ?", (int(task_id),))
            conn.commit()
            if cur.rowcount == 0:
                return {"success": False, "error": f"Task #{task_id} not found."}

        return {"success": True, "task_id": task_id, "message": f"Task #{task_id} removed, Sir."}

    def get_summary(self) -> Dict[str, Any]:
        """Summary of active tasks."""
        with self._get_connection() as conn:
            todo = conn.execute("SELECT COUNT(*) FROM task_board WHERE status = 'todo'").fetchone()[0]
            in_prog = conn.execute("SELECT COUNT(*) FROM task_board WHERE status = 'in_progress'").fetchone()[0]
            done = conn.execute("SELECT COUNT(*) FROM task_board WHERE status = 'done'").fetchone()[0]

        return {
            "todo": todo,
            "in_progress": in_prog,
            "done": done,
            "total": todo + in_prog + done,
            "summary_text": f"You have {todo} pending tasks, {in_prog} in progress, and {done} completed."
        }


task_board = TaskBoard()
