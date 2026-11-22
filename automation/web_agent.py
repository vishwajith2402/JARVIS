"""
Agentic Web Scraper & Autonomous File Downloader for TITAN.
Capabilities:
1. Resilient streaming file downloader with size calculation and progress tracking.
2. Web table & structured data extraction using BeautifulSoup4.
3. Live news & topic aggregation.
100% Free & Local.
"""

import os
import re
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup

DOWNLOAD_DIR = Path(r"D:\Practice Projects\JARVIS\data\downloads")
try:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass


class WebAgent:
    def __init__(self, download_dir: Path = DOWNLOAD_DIR):
        self.download_dir = download_dir

    def download_file(self, url: str, custom_filename: Optional[str] = None) -> Dict[str, Any]:
        """Downloads any remote file (PDF, dataset, zip, audio, code) to local storage."""
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"

        try:
            # Determine filename
            if custom_filename:
                filename = custom_filename
            else:
                parsed = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed.path) or "downloaded_file"
                if not os.path.splitext(filename)[1]:
                    filename += ".bin"

            save_path = self.download_dir / filename

            # Fetch with realistic browser user-agent
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )

            total_bytes = 0
            with urllib.request.urlopen(req, timeout=45) as response, open(save_path, "wb") as out_file:
                chunk_size = 64 * 1024  # 64 KB
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    total_bytes += len(chunk)

            size_mb = round(total_bytes / (1024 * 1024), 2)
            msg = f"Download complete, Sir. Saved '{filename}' ({size_mb} MB) to downloads directory."

            return {
                "success": True,
                "file_name": filename,
                "file_path": str(save_path.resolve()),
                "size_mb": size_mb,
                "message": msg
            }

        except Exception as e:
            return {"success": False, "error": f"Download failed: {e}"}

    def scrape_web_tables_and_links(self, url: str) -> Dict[str, Any]:
        """Extracts structured tables, headlines, and main content from any webpage."""
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                html = resp.read().decode("utf-8", errors="replace")

            soup = BeautifulSoup(html, "html.parser")
            title = soup.title.string.strip() if soup.title else url

            # Extract headings
            headings = [h.get_text().strip() for h in soup.find_all(["h1", "h2", "h3"]) if h.get_text().strip()][:10]

            # Extract tables
            extracted_tables = []
            for table in soup.find_all("table")[:3]:
                rows = []
                for tr in table.find_all("tr"):
                    cols = [td.get_text().strip() for td in tr.find_all(["td", "th"])]
                    if cols:
                        rows.append(cols)
                if rows:
                    extracted_tables.append(rows[:10])

            # Clean body text
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.extract()
            body_text = soup.get_text(separator=" ", strip=True)[:3000]

            return {
                "success": True,
                "title": title,
                "url": url,
                "headings": headings,
                "tables_count": len(extracted_tables),
                "tables": extracted_tables,
                "summary_text": body_text[:1200]
            }

        except Exception as e:
            return {"success": False, "error": f"Scraping failed: {e}"}


web_agent = WebAgent()
