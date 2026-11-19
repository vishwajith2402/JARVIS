"""
Web Researcher for JARVIS.
Conducts free, privacy-first web searches and technical documentation queries.
"""

import json
import urllib.parse
import urllib.request
from typing import Any, Dict, List


class WebResearcher:
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Search DuckDuckGo instant API or HTML endpoints without requiring API keys."""
        results = []
        try:
            # Use DuckDuckGo Instant Answer API
            encoded = urllib.parse.quote(query)
            url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) JARVIS/1.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))

                if data.get("Abstract"):
                    results.append({
                        "title": data.get("Heading", query),
                        "snippet": data.get("Abstract"),
                        "url": data.get("AbstractURL", "")
                    })

                for topic in data.get("RelatedTopics", []):
                    if "Text" in topic and "FirstURL" in topic:
                        results.append({
                            "title": topic.get("Text")[:60] + "...",
                            "snippet": topic.get("Text"),
                            "url": topic.get("FirstURL")
                        })
                    if len(results) >= max_results:
                        break
        except Exception as e:
            results.append({
                "title": f"Search fallback for '{query}'",
                "snippet": f"Web connection error or offline: {e}",
                "url": ""
            })

        return results


web_researcher = WebResearcher()
