"""
Executive Profile & Knowledge Graph Memory for TITAN (Top MNC Caliber).
Stores user identity, developer persona, preferred stacks, VIP projects,
habits, and permanent facts. Provides dynamic context injection for the LLM.
100% Free & Local.
"""

import time
import json
from typing import Any, Dict, List, Optional
from core.memory import memory


class ExecutiveProfileManager:
    DEFAULT_PROFILE = {
        "user_name": "Vishwajith",
        "user_title": "Sir",
        "role": "Lead Software Engineer & AI Architect",
        "organization": "Independent / Innovation Labs",
        "preferred_languages": ["Python", "JavaScript", "TypeScript", "PowerShell"],
        "primary_ide": "Visual Studio Code",
        "hardware": "HP Victus 15 (AMD Ryzen 5 5600H, NVIDIA RTX 3050, 16GB RAM)",
        "work_style": "Concise, highly technical, tactical, results-oriented",
        "vip_projects": ["JARVIS", "TITAN", "Practice Projects"]
    }

    def __init__(self):
        self._ensure_default_profile()

    def _ensure_default_profile(self) -> None:
        """Seed default executive profile if not already present."""
        existing = memory.get_preference("executive_profile", None)
        if not existing or not isinstance(existing, dict):
            memory.set_preference("executive_profile", self.DEFAULT_PROFILE)

    def get_profile(self) -> Dict[str, Any]:
        """Retrieve full executive profile."""
        prof = memory.get_preference("executive_profile", self.DEFAULT_PROFILE)
        if isinstance(prof, str):
            try:
                prof = json.loads(prof)
            except Exception:
                prof = self.DEFAULT_PROFILE
        return prof

    def update_profile(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update fields in the executive profile."""
        prof = self.get_profile()
        prof.update(updates)
        memory.set_preference("executive_profile", prof)
        return {"success": True, "profile": prof}

    def remember_fact(self, category: str, subject: str, fact: str) -> Dict[str, Any]:
        """Store a permanent knowledge fact about the user, projects, or workflow."""
        with memory._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO facts (category, subject, fact, created_at) VALUES (?, ?, ?, ?)",
                (category, subject, fact, time.time())
            )
            fact_id = cur.lastrowid
            conn.commit()
            return {"success": True, "fact_id": fact_id, "message": f"Remembered: [{category}] {subject} - {fact}"}

    def recall_facts(self, search_term: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve stored knowledge facts, optionally filtered."""
        with memory._get_connection() as conn:
            cur = conn.cursor()
            if search_term and search_term.strip():
                term = f"%{search_term.strip()}%"
                cur.execute(
                    "SELECT id, category, subject, fact, created_at FROM facts WHERE subject LIKE ? OR fact LIKE ? OR category LIKE ? ORDER BY id DESC LIMIT 25",
                    (term, term, term)
                )
            else:
                cur.execute(
                    "SELECT id, category, subject, fact, created_at FROM facts ORDER BY id DESC LIMIT 25"
                )
            rows = cur.fetchall()
            return [dict(r) for r in rows]

    def forget_fact(self, fact_id: int) -> Dict[str, Any]:
        """Remove a fact by ID."""
        with memory._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM facts WHERE id = ?", (fact_id,))
            conn.commit()
            return {"success": True, "message": f"Fact #{fact_id} removed from memory."}

    def build_executive_context(self) -> str:
        """Constructs an executive prompt injection to personalize the assistant."""
        prof = self.get_profile()
        facts = self.recall_facts()
        facts_summary = ""
        if facts:
            facts_list = [f"- [{f['category'].upper()}] {f['subject']}: {f['fact']}" for f in facts[:8]]
            facts_summary = "\nKnown Executive Facts & Preferences:\n" + "\n".join(facts_list)

        return f"""Executive Profile:
- Principal: {prof.get('user_name', 'Vishwajith')} (Address as: {prof.get('user_title', 'Sir')})
- Role: {prof.get('role', 'Lead Developer')}
- Stacks: {', '.join(prof.get('preferred_languages', ['Python']))}
- Primary IDE: {prof.get('primary_ide', 'VS Code')}
- Work Style: {prof.get('work_style', 'Concise & tactical')}
{facts_summary}
"""


executive_profile = ExecutiveProfileManager()
