"""Step 5: Pinterest Pin Generator."""
from dataclasses import dataclass, field
from typing import List
from src.modules.article_generator import Article

@dataclass
class Pin:
    title: str
    description: str
    image_url: str
    destination_url: str  # Always article slug, NEVER direct affiliate
    board: str = ""

class PinterestAssetCreator:
    def create_pins(self, article: Article, images: list) -> List[Pin]:
        pins = []
        for i, img in enumerate(images[:2]):
            pins.append(Pin(
                title=article.title[:100],
                description=article.meta_description[:500],
                image_url=img.get("url") or img.get("path") or "",
                destination_url="",  # Will be set by blogger_publisher after publish
            ))
        return pins
