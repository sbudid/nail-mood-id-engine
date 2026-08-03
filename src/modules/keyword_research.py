"""Step 1 & 2: Keyword Research via 9Router Mode3."""
from dataclasses import dataclass, field
from typing import List
import json
import re
import requests
import os

ROUTER_URL = "http://localhost:20128/v1/chat/completions"
ROUTER_KEY = os.getenv("ROUTER_API_KEY", "sk-6b3ac6ef8e3b70c9-nta99q-76eae469")

@dataclass
class SEOPlan:
    primary_keyword: str
    secondary_keywords: List[str] = field(default_factory=list)
    long_tail_keywords: List[str] = field(default_factory=list)
    search_intent: str = "informational"
    category: str = ""


class KeywordResearcher:
    def generate_plan(self, topic: str, category: str = "") -> SEOPlan:
        prompt = f"""Generate 20 SEO keywords in Indonesian about "{topic}" for a nail beauty blog.

Return ONLY a JSON array of strings, no explanation. Example:
["keyword1", "keyword2", "keyword3"]

Mix of:
- 5 primary keywords (2-3 words)
- 5 question keywords (starts with "apa", "cara", "kenapa", "tips")
- 5 long-tail keywords (4+ words)
- 5 trend keywords (2026, terbaru, viral)"""

        try:
            resp = requests.post(ROUTER_URL, json={
                "model": "Mode3",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2048,
                "temperature": 0.7,
                "stream": False
            }, headers={"Authorization": f"Bearer {ROUTER_KEY}", "Content-Type": "application/json"}, timeout=60)
            
            data = resp.json()
            msg = data["choices"][0]["message"]
            content = msg.get("content") or msg.get("reasoning") or ""
            
            # Parse JSON array
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                try:
                    keywords = json.loads(match.group())
                except json.JSONDecodeError:
                    keywords = re.findall(r'"([^"]+)"', match.group())
            else:
                keywords = re.findall(r'"([^"]+)"', content)
            
            keywords = [k.strip() for k in keywords if len(k.strip()) > 3]
            primary = topic.lower().strip()
            
            return SEOPlan(
                primary_keyword=primary,
                secondary_keywords=keywords[:5],
                long_tail_keywords=keywords[5:10],
                search_intent="informational",
                category=category,
            )
        except Exception as e:
            print(f"Keyword gen error: {e}")
            return SEOPlan(primary_keyword=topic.lower().strip())
