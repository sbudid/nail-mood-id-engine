"""
Hermes Nail Mood Engine — Full Pipeline with Publish
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.modules.keyword_research import KeywordResearcher, SEOPlan
from src.modules.article_generator import ArticleWriter
from src.core.token_optimizer import ImageAssetResolver
from src.modules.pinterest_generator import PinterestAssetCreator
from src.modules.blogger_publisher import BloggerPublisher
from src.utils.logger import get_logger
from src.utils.file_handler import load_yaml

log = get_logger("engine")


class NailMoodEngine:
    def __init__(self, config: dict):
        self.config = config
        self.project_root = config.get("project_root", ".")
        self.image_resolver = ImageAssetResolver(self.project_root)

    def run_pipeline(self, topic: str, max_articles: int = 1, publish: bool = True) -> list:
        results = []
        
        for i in range(max_articles):
            log.info(f"Article {i+1}/{max_articles}: {topic}")
            
            # STEP 1-2: Keywords
            seo_plan = KeywordResearcher().generate_plan(topic)
            log.info(f"  Keywords: {seo_plan.secondary_keywords[:3]}...")
            
            # STEP 3: Article
            article = ArticleWriter().write(seo_plan)
            if article.title == "Error":
                log.warning("  Article generation failed, skipping")
                continue
            log.info(f"  Title: {article.title}")
            
            # STEP 4: Image resolution
            images = []
            for ctx in article.required_images:
                resolved = self.image_resolver.resolve_image(seo_plan.primary_keyword, ctx)
                images.append(resolved)
            
            # STEP 5-6: Pinterest + Shopee (placeholder)
            pins = PinterestAssetCreator().create_pins(article, images)
            
            # STEP 7-8: SEO schema
            # (built into article via H2/FAQ structure)
            
            # STEP 9-10: Publish
            result = {"title": article.title, "words": len(article.content_html.split())}
            if publish:
                labels = [l.strip().title() for l in seo_plan.secondary_keywords[:3]]
                labels += [article.title.split(":")[0].strip() if ":" in article.title else "Nail Tips"]
                pub = BloggerPublisher().publish(article, labels=labels)
                result.update(pub)
                log.info(f"  Published: {pub.get('url', 'FAILED')}")
            else:
                result["status"] = "draft"
            
            results.append(result)
        
        return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--max", type=int, default=1)
    parser.add_argument("--no-publish", action="store_true")
    args = parser.parse_args()

    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "settings.yaml")
    config = load_yaml(config_path) or {}
    config["project_root"] = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    engine = NailMoodEngine(config)
    results = engine.run_pipeline(args.topic, max_articles=args.max, publish=not args.no_publish)
    print(f"\nDone: {len(results)} articles")
    for r in results:
        url = r.get("url", "N/A")
        print(f"  {r['title'][:60]} -> {url}")
