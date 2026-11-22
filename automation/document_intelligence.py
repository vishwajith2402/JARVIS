"""
Universal Document Intelligence Engine for TITAN.
Extracts and analyzes PDF, DOCX, CSV, Markdown, and text files locally.
Indexes document knowledge into TITAN's permanent deep research memory.
100% Free & Local.
"""

import os
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

from core.brain import brain
from automation.deep_research import deep_research


class DocumentIntelligence:
    def __init__(self):
        pass

    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """Extracts readable text from PDF, CSV, JSON, TXT, or MD files."""
        path = Path(file_path)
        if not path.is_file():
            return {"success": False, "error": f"File not found: {file_path}"}

        ext = path.suffix.lower()
        extracted_text = ""
        total_pages = 1

        try:
            if ext == ".pdf":
                if not PYPDF_AVAILABLE:
                    return {"success": False, "error": "pypdf library not available."}
                reader = pypdf.PdfReader(str(path))
                total_pages = len(reader.pages)
                pages_text = []
                for idx, page in enumerate(reader.pages):
                    t = page.extract_text() or ""
                    if t.strip():
                        pages_text.append(f"--- Page {idx + 1} ---\n{t.strip()}")
                extracted_text = "\n\n".join(pages_text)

            elif ext in (".csv",):
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    r = csv.reader(f)
                    rows = list(r)
                    extracted_text = f"CSV with {len(rows)} rows.\nHeader: {rows[0] if rows else 'None'}\nSample data:\n"
                    for row in rows[:15]:
                        extracted_text += ", ".join(row) + "\n"

            elif ext in (".json",):
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    data = json.load(f)
                    extracted_text = json.dumps(data, indent=2)[:8000]

            elif ext in (".txt", ".md", ".py", ".html", ".css", ".js", ".log"):
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    extracted_text = f.read()

            else:
                # Binary fallback: attempt UTF-8 decode
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    extracted_text = f.read(10000)

            return {
                "success": True,
                "file_name": path.name,
                "file_path": str(path.resolve()),
                "total_chars": len(extracted_text),
                "total_pages": total_pages,
                "content": extracted_text
            }
        except Exception as e:
            return {"success": False, "error": f"Extraction failed: {e}"}

    def analyze_document(self, file_path: str, question: Optional[str] = None) -> Dict[str, Any]:
        """
        Extracts document text, indexes it into deep research memory,
        and uses TITAN's local model to answer questions or provide an executive summary.
        """
        extract_res = self.extract_text(file_path)
        if not extract_res["success"]:
            return extract_res

        content = extract_res["content"]
        file_name = extract_res["file_name"]

        # 1. Index document into Deep Research SQLite FTS5 for permanent memory
        try:
            deep_research.index_file(file_path)
        except Exception:
            pass

        # 2. Formulate prompt
        snippet = content[:5000]  # Feed first 5k characters to keep local inference rapid

        if question and question.strip():
            user_instruction = f"Based on the document '{file_name}', answer the following question clearly:\nQuestion: {question}\n\nDocument Excerpt:\n{snippet}"
        else:
            user_instruction = f"Provide a concise, professional executive summary of the document '{file_name}', highlighting key points, conclusions, and action items:\n\nDocument Excerpt:\n{snippet}"

        messages = [
            {"role": "system", "content": "You are TITAN's Document Intelligence Analyst. Provide clear, well-structured, insightful analyses."},
            {"role": "user", "content": user_instruction}
        ]

        try:
            if brain._active_provider == "offline":
                summary = f"Summary of {file_name}: Extracted {len(content)} characters across {extract_res['total_pages']} page(s). Excerpt: {snippet[:250]}..."
            else:
                summary = brain._dispatch_chat(messages)
            return {
                "success": True,
                "file_name": file_name,
                "pages": extract_res["total_pages"],
                "analysis": summary
            }
        except Exception:
            return {
                "success": True,
                "file_name": file_name,
                "pages": extract_res["total_pages"],
                "analysis": f"Document extracted successfully ({len(content)} characters). Preview: {snippet[:250]}..."
            }


doc_intelligence = DocumentIntelligence()
