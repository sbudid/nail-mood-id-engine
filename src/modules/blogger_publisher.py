"""Step 9 & 10: Blogger HTML Generator + Publisher."""
from src.modules.article_generator import Article
from src.modules.seo_enhancer import SEOEnhancer

class BloggerHTMLGenerator:
    def build(self, article: Article, images: list, pins: list, schema_type: str = "FAQPage") -> dict:
        seo = SEOEnhancer()
        faq_schema = seo.build_faq_schema(article) if schema_type == "FAQPage" else ""
        meta_tags = seo.build_meta_tags(article)

        html = f"""<!DOCTYPE html>
<html>
<head>
  {meta_tags}
  <script type="application/ld+json">{faq_schema}</script>
</head>
<body>
  <article>
    {article.content_html}
  </article>
</body>
</html>"""

        return {
            "html": html,
            "title": article.title,
            "images": images,
            "pins": pins,
            "faq_schema": faq_schema,
        }

    def export(self, package: dict, output_dir: str = "data/Published"):
        import os
        os.makedirs(output_dir, exist_ok=True)
        filename = package["title"].lower().replace(" ", "-")[:50]
        with open(os.path.join(output_dir, f"{filename}.html"), "w", encoding="utf-8") as f:
            f.write(package["html"])
        return {"status": "exported", "path": f"{output_dir}/{filename}.html"}
