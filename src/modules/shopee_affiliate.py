"""Step 6: Shopee Affiliate Link Builder."""
import os

SHOPEE_DISCLAIMER = (
    "Disclaimer: Artikel ini mengandung link afiliasi Shopee. "
    "Kami mendapat komisi kecil jika Anda membeli melalui link tersebut "
    "tanpa biaya tambahan untuk Anda."
)

class ShopeeAffiliateBuilder:
    def __init__(self, affiliate_id: str = ""):
        self.affiliate_id = affiliate_id or os.getenv("SHOPEE_AFFILIATE_ID", "")

    def build_link(self, product_url: str) -> str:
        if not self.affiliate_id:
            return product_url
        separator = "&" if "?" in product_url else "?"
        return f"{product_url}{separator}af_id={self.affiliate_id}"

    def get_disclaimer(self) -> str:
        return SHOPEE_DISCLAIMER
