"""
Hermes Automation Engine — Main Orchestrator
Modular design for future multi-platform support (WordPress, Ghost, etc.)
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.modules.keyword_research import KeywordResearcher
from src.modules.article_generator import ArticleWriter
from src.core.token_optimizer import ImageAssetResolver
from src.modules.pinterest_generator import PinterestAssetCreator
from src.modules.blogger_publisher import BloggerHTMLGenerator
from src.utils.logger import get_logger
from src.utils.file_handler import load_yaml

log = get_logger("orchestrator")


class NailMoodEngine:
    def __init__(self, config: dict):
        self.config = config
        self.project_root = config.get("project_root", ".")
        self.image_resolver = ImageAssetResolver(self.project_root)

    async def run_pipeline(self, topic: str) -> dict:
        log.info(f"Pipeline start: {topic}")

        # STEP 1-2: Keyword & SEO Planning
        seo_plan = await KeywordResearcher().generate_plan(topic)
        log.info(f"SEO plan: {seo_plan.primary_keyword}")

        # STEP 3: Article Generation (Human-sounding, EEAT)
        article = await ArticleWriter().write(
            seo_plan=seo_plan,
            style="natural_pinterest_friendly",
            word_count=(1500, 2500),
        )
        log.info(f"Article: {article.title}")

        # STEP 4: Smart Image Pipeline (Token Optimized)
        images = []
        for img_context in article.required_images:
            resolved = await self.image_resolver.resolve_image(
                keyword=seo_plan.primary_keyword,
                context=img_context,
            )
            images.append(resolved)
        log.info(f"Images resolved: {len(images)} (AI used: {sum(1 for i in images if i.get('ai_used'))})")

        # STEP 5-6: Pinterest Pins & Shopee Recommendations
        pins = PinterestAssetCreator().create_pins(article, images)
        log.info(f"Pins created: {len(pins)}")

        # STEP 7-9: SEO Schema & Blogger HTML
        publisher = BloggerHTMLGenerator()
        html_package = publisher.build(
            article=article,
            images=images,
            pins=pins,
            schema_type="FAQPage",
        )

        # STEP 10: Export
        result = publisher.export(html_package)
        log.info(f"Exported: {result['path']}")
        return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Nail Mood ID Engine")
    parser.add_argument("--topic", required=True, help="Main topic")
    parser.add_argument("--max", type=int, default=1, help="Max articles")
    args = parser.parse_args()

    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "settings.yaml")
    config = load_yaml(config_path) or {}
    config["project_root"] = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    engine = NailMoodEngine(config)
    result = asyncio.run(engine.run_pipeline(args.topic))
    print(f"Done: {result}")
