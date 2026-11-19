"""
Auto-Update Manager for JARVIS.
Checks GitHub repository or GitHub Releases for new updates, features, and patches.
Supports auto-pull for development and version checks for packaged releases.
"""

import json
import subprocess
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional
from config.config_manager import config

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class UpdateManager:
    def __init__(self):
        self.current_version = config.get("system", "version", "1.1.0")
        self.github_repo = config.get("system", "github_repo", "vishwajith2402/JARVIS")

    def check_git_updates(self) -> Dict[str, Any]:
        """Check if local git repository is behind remote origin/main."""
        try:
            # Fetch remote without modifying working directory
            fetch_res = subprocess.run(
                ["git", "fetch"],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
            if fetch_res.returncode != 0:
                return {"has_update": False, "error": "Git remote unreachable or git not configured."}

            # Compare local HEAD with origin/main
            status_res = subprocess.run(
                ["git", "rev-list", "HEAD..origin/main", "--count"],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
            count = int(status_res.stdout.strip()) if status_res.stdout.strip().isdigit() else 0
            return {
                "has_update": count > 0,
                "commits_behind": count,
                "message": f"{count} new commits available from GitHub." if count > 0 else "Up to date."
            }
        except Exception as e:
            return {"has_update": False, "error": str(e)}

    def apply_git_update(self) -> Dict[str, Any]:
        """Pull latest changes from GitHub."""
        try:
            pull_res = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=str(PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=20,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
            )
            if pull_res.returncode == 0:
                return {"success": True, "output": pull_res.stdout.strip()}
            return {"success": False, "error": pull_res.stderr.strip()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_github_release(self, repo_owner: str, repo_name: str) -> Dict[str, Any]:
        """Check GitHub Releases API for a newer packaged release tag."""
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        try:
            req = urllib.request.Request(
                api_url,
                headers={"User-Agent": "JARVIS-AutoUpdater/1.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                tag = data.get("tag_name", "").lstrip("v")
                html_url = data.get("html_url", "")
                notes = data.get("body", "")

                has_update = tag and tag != self.current_version
                return {
                    "has_update": has_update,
                    "latest_version": tag,
                    "current_version": self.current_version,
                    "release_notes": notes[:300] + "..." if len(notes) > 300 else notes,
                    "download_url": html_url
                }
        except Exception as e:
            return {"has_update": False, "error": f"Could not check release: {e}"}


updater = UpdateManager()
