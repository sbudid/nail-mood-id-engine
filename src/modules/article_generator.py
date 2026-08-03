"""Step 3: Article Generation (Human-sounding, EEAT-compliant)."""
from dataclasses import dataclass, field
from typing import List
from src.modules.keyword_research import SEOPlan

@dataclass
class Article:
    title: str
    content_html: str
    meta_description: str
    required_images: List[dict] = field(default_factory=list)
    faq_items: List[dict] = field(default_factory=list)
    shopee_links: List[dict] = field(default_factory=list)

class ArticleWriter:
    def __init__(self):
        self.prompt_template = (
            "Tulis artikel panjang (1500-2500 kata) tentang {keyword} dalam Bahasa Indonesia. "
            "Gaya: natural, seperti teman yang berbagi tips. "
            "Sertakan: H2 headings, FAQ section, disclaimer Shopee affiliate jika ada produk. "
            "Gunakan markdown format."
        )

    async def write(self, seo_plan: SEOPlan, style: str = "natural_pinterest_friendly",
                    word_count: tuple = (1500, 2500)) -> Article:
        """Generate article. TODO: integrate LLM API for real generation."""
        # Placeholder — will call 9Router / OpenAI in real implementation
        return Article(
            title=f"Tips {seo_plan.primary_keyword.title()} Terbaik untuk Pemula",
            content_html="<h2>Intro</h2><p>Coming soon...</p>",
            meta_description=f"Panduan lengkap {seo_plan.primary_keyword} untuk pemula.",
        )
