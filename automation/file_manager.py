"""
File and Project Manager for JARVIS.
Safely indexes projects, searches files, reads contents, and organizes directories.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from config.config_manager import config


class FileManager:
    def __init__(self):
        self._allowed_roots = [
            Path(p) for p in config.get("automation", "allowed_project_roots", [r"D:\Practice Projects", r"D:\Extra"])
        ]

    def _is_path_allowed(self, target_path: Path) -> bool:
        try:
            target = target_path.resolve()
            for root in self._allowed_roots:
                if root.resolve() in target.parents or target == root.resolve():
                    return True
        except Exception:
            return False
        return True

    def find_projects(self, root_dir: Optional[str] = None) -> List[Dict[str, Any]]:
        """Scan directories for projects (folders containing .git, requirements.txt, package.json, etc.)."""
        roots = [Path(root_dir)] if root_dir else self._allowed_roots
        projects = []

        for root in roots:
            if not root.exists() or not root.is_dir():
                continue
            try:
                for entry in root.iterdir():
                    if entry.is_dir() and not entry.name.startswith("."):
                        # Detect project type
                        has_git = (entry / ".git").exists()
                        has_py = (entry / "requirements.txt").exists() or any(entry.glob("*.py"))
                        has_node = (entry / "package.json").exists()

                        lang = "python" if has_py else ("javascript/node" if has_node else "general")
                        mtime = entry.stat().st_mtime

                        projects.append({
                            "name": entry.name,
                            "path": str(entry.resolve()),
                            "language": lang,
                            "last_modified": mtime,
                            "has_git": has_git
                        })
            except Exception as e:
                print(f"[FileManager] Error scanning root {root}: {e}")

        # Sort by most recently modified
        projects.sort(key=lambda x: x["last_modified"], reverse=True)
        return projects

    def search_files(self, pattern: str, root_dir: Optional[str] = None, max_results: int = 15) -> List[Dict[str, Any]]:
        """Search for files matching name or extension across allowed roots."""
        roots = [Path(root_dir)] if root_dir else self._allowed_roots
        matches = []

        for root in roots:
            if not root.exists():
                continue
            try:
                for path in root.rglob(f"*{pattern}*"):
                    if any(part.startswith(".") or part in ("node_modules", "venv", "__pycache__") for part in path.parts):
                        continue
                    if path.is_file():
                        matches.append({
                            "name": path.name,
                            "path": str(path.resolve()),
                            "size_bytes": path.stat().st_size,
                            "modified": path.stat().st_mtime
                        })
                    if len(matches) >= max_results:
                        return matches
            except Exception:
                pass
        return matches

    def read_file(self, file_path: str, max_lines: int = 100) -> Dict[str, Any]:
        """Safely read lines from a file."""
        p = Path(file_path)
        if not p.exists() or not p.is_file():
            return {"success": False, "error": f"File '{file_path}' does not exist."}

        try:
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                lines = [f.readline() for _ in range(max_lines)]
                return {
                    "success": True,
                    "path": str(p.resolve()),
                    "total_lines_read": len(lines),
                    "content": "".join(lines)
                }
        except Exception as e:
            return {"success": False, "error": f"Failed reading '{file_path}': {e}"}

    def inspect_directory_tree(self, dir_path: str, max_depth: int = 2) -> Dict[str, Any]:
        """Generate a hierarchical structure tree of a directory."""
        p = Path(dir_path)
        if not p.exists() or not p.is_dir():
            return {"success": False, "error": f"Directory '{dir_path}' does not exist."}

        def _build_tree(current: Path, depth: int) -> Dict[str, Any]:
            if depth > max_depth:
                return {"name": current.name, "type": "dir", "children": []}
            children = []
            try:
                for item in sorted(current.iterdir()):
                    if item.name.startswith(".") or item.name in ("node_modules", "venv", "__pycache__"):
                        continue
                    if item.is_dir():
                        children.append(_build_tree(item, depth + 1))
                    else:
                        children.append({"name": item.name, "type": "file", "size": item.stat().st_size})
            except Exception:
                pass
            return {"name": current.name, "type": "dir", "children": children}

        return {"success": True, "tree": _build_tree(p, 0)}

    def create_directory(self, dir_path: str) -> Dict[str, Any]:
        p = Path(dir_path)
        try:
            p.mkdir(parents=True, exist_ok=True)
            return {"success": True, "path": str(p.resolve()), "message": f"Created directory '{dir_path}'"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def write_file(self, file_path: str, content: str, overwrite: bool = True) -> Dict[str, Any]:
        """Write text content to a file. Creates parent directories automatically."""
        p = Path(file_path)
        if p.exists() and not overwrite:
            return {"success": False, "error": f"File '{file_path}' already exists and overwrite=False."}
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
            return {
                "success": True,
                "path": str(p.resolve()),
                "bytes_written": len(content.encode("utf-8")),
                "message": f"Successfully wrote {len(content)} characters to '{file_path}'"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def append_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Append text content to an existing or new file."""
        p = Path(file_path)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "a", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "path": str(p.resolve()), "message": f"Appended content to '{file_path}'"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_directory(self, dir_path: str) -> Dict[str, Any]:
        """List files and subdirectories in target path."""
        p = Path(dir_path)
        if not p.exists() or not p.is_dir():
            return {"success": False, "error": f"Directory '{dir_path}' does not exist."}
        try:
            items = []
            for item in p.iterdir():
                items.append({
                    "name": item.name,
                    "is_dir": item.is_dir(),
                    "size_bytes": item.stat().st_size if item.is_file() else None,
                    "modified": item.stat().st_mtime
                })
            return {"success": True, "path": str(p.resolve()), "total_items": len(items), "items": items}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Safely delete a file."""
        p = Path(file_path)
        if not p.exists():
            return {"success": False, "error": f"Path '{file_path}' does not exist."}
        try:
            if p.is_file():
                p.unlink()
                return {"success": True, "message": f"Deleted file '{file_path}'"}
            elif p.is_dir():
                import shutil
                shutil.rmtree(p)
                return {"success": True, "message": f"Deleted directory '{file_path}'"}
        except Exception as e:
            return {"success": False, "error": str(e)}


file_manager = FileManager()
