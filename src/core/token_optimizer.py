"""
Token Optimizer: Enforces the Image Priority Hierarchy
Priority: Existing Assets > Free Stock > Shopee Images > AI Generation
"""
import os
from typing import Optional, Dict
import httpx

class ImageAssetResolver:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.existing_path = os.path.join(project_root, "data/Images/existing")

    async def resolve_image(self, keyword: str, context: dict) -> Dict[str, str]:
        """Returns image source based on strict priority. AI = last resort."""
        existing = self._check_existing(keyword)
        if existing:
            return {"source": "existing", "path": existing, "ai_used": False}

        stock = await self._search_free_stock(keyword)
        if stock:
            return {"source": "free_stock", "url": stock, "ai_used": False}

        shopee_img = context.get("shopee_product_image")
        if shopee_img:
            return {"source": "shopee", "url": shopee_img, "ai_used": False}

        return {
            "source": "ai_generated",
            "prompt": self._build_pinterest_prompt(keyword),
            "ai_used": True,
            "ratio": "1000x1500",
        }

    def _check_existing(self, keyword: str) -> Optional[str]:
        if not os.path.exists(self.existing_path):
            return None
        keyword_clean = keyword.lower().replace(" ", "_")
        for f in os.listdir(self.existing_path):
            if keyword_clean in f.lower():
                return os.path.join(self.existing_path, f)
        return None

    async def _search_free_stock(self, keyword: str) -> Optional[str]:
        unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY")
        if not unsplash_key:
            return None
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.unsplash.com/search/photos",
                    params={"query": keyword, "per_page": 1},
                    headers={"Authorization": f"Client-ID {unsplash_key}"},
                    timeout=10,
                )
                data = resp.json()
                if data.get("results"):
                    return data["results"][0]["urls"]["regular"]
        except Exception:
            pass
        return None

    def _build_pinterest_prompt(self, keyword: str) -> str:
        return (
            f"Vertical photorealistic luxury nail photography of {keyword}. "
            f"Professional studio lighting, no watermark, no text, high detail."
        )
