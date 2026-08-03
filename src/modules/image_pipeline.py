"""Step 4: Image Pipeline — delegates to Token Optimizer."""
from src.core.token_optimizer import ImageAssetResolver

class ImagePipeline:
    def __init__(self, resolver: ImageAssetResolver):
        self.resolver = resolver

    async def process(self, keyword: str, contexts: list) -> list:
        results = []
        for ctx in contexts:
            resolved = await self.resolver.resolve_image(keyword, ctx)
            results.append(resolved)
        return results
