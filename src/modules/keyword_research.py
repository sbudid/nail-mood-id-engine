"""Step 1 & 2: Keyword Research & SEO Planning."""
from dataclasses import dataclass, field
from typing import List
import httpx

@dataclass
class SEOPlan:
    primary_keyword: str
    secondary_keywords: List[str] = field(default_factory=list)
    long_tail_keywords: List[str] = field(default_factory=list)
    search_intent: str = "informational"
    category: str = ""

class KeywordResearcher:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key

    async def generate_plan(self, topic: str, category: str = "") -> SEOPlan:
        """Generate SEO plan for a topic."""
        # TODO: integrate real keyword data source (Google Suggest, Ahrefs API)
        primary = topic.lower().strip()
        plan = SEOPlan(
            primary_keyword=primary,
            secondary_keywords=[f"{primary} tips", f"{primary} 2026", f"cara {primary}"],
            long_tail_keywords=[
                f"cara {primary} untuk pemula",
                f"tips {primary} tahan lama",
                f"rekomendasi {primary} terbaik",
            ],
            search_intent="informational",
            category=category,
        )
        return plan
