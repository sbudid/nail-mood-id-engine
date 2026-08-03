"""Step 7 & 8: SEO Schema + Meta Enhancement."""
import json
from src.modules.article_generator import Article

class SEOEnhancer:
    def build_faq_schema(self, article: Article) -> str:
        faq_entities = []
        for item in article.faq_items:
            faq_entities.append({
                "@type": "Question",
                "name": item.get("question", ""),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item.get("answer", ""),
                },
            })
        schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_entities,
        }
        return json.dumps(schema, ensure_ascii=False, indent=2)

    def build_meta_tags(self, article: Article) -> str:
        return (
            f'<meta name="description" content="{article.meta_description}">\n'
            f'<meta property="og:title" content="{article.title}">\n'
            f'<meta property="og:type" content="article">'
        )
