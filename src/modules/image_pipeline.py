"""Image pipeline — uses Pollinations.ai (free) with prompts from master xlsx."""
import os
import re
import urllib.parse
import urllib.request
import logging

logger = logging.getLogger("engine.image")


def generate_image(prompt: str, save_path: str = "", width: int = 1000, height: int = 1500) -> str:
    """Generate image via Pollinations.ai. Returns public URL."""
    clean_prompt = re.sub(r"<[^>]+>", "", prompt).strip()
    if len(clean_prompt) < 10:
        clean_prompt = "beautiful nail art, close up, elegant, glossy finish, clean background"

    encoded = urllib.parse.quote(clean_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true"
    logger.info(f"Image URL: {url[:80]}...")
    return url


def resolve_images(article, topic: str, pin_data: dict = None) -> list:
    """Resolve images: Pollinations AI using prompts from xlsx or fallback."""
    images = []
    save_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "Images")
    os.makedirs(save_dir, exist_ok=True)

    # Get prompt from pin_data if available
    prompt = pin_data.get("image_prompt", "") if pin_data else ""
    if not prompt:
        prompt = f"Vertical Pinterest beauty editorial, 2:3. Close-up of {topic} nails, realistic, glossy finish, clean background, elegant, beauty editorial style"

    import random
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower())[:40]
    variations = [
        (prompt, "close-up, beauty editorial"),
        (prompt.replace("close-up", "flat lay") + ", overhead shot, lifestyle", "flat lay"),
        (prompt.replace("editorial", "natural lighting") + ", different angle, soft focus", "angle"),
        (prompt + ", detail shot, macro lens", "detail"),
        (prompt.replace("2:3", "1:1").replace("vertical", "square") + ", studio lighting, clean background", "studio"),
        (prompt + ", on marble surface, aesthetic, minimal", "lifestyle"),
        (prompt.replace("close-up", "hands together") + ", symmetrical, both hands, elegant pose", "both hands"),
    ]

    for i, (variation_prompt, suffix) in enumerate(variations[:6]):
        seed = random.randint(1000, 99999)
        variation_prompt += f", seed {seed}"
        result = generate_image(variation_prompt)
        if result:
            images.append({"local": result, "alt": f"{topic} — {suffix}"})
        if len(images) >= 5:
            break

    return images


def load_pin_data(xlsx_path: str, topic: str) -> dict:
    """Match topic to pin data from master xlsx for image prompts."""
    try:
        import openpyxl
        wb = openpyxl.load_workbook(xlsx_path)
        ws = wb["Pin_Content_60"]
        topic_lower = topic.lower()

        for row in ws.iter_rows(values_only=True):
            if not row[0] or not str(row[0]).startswith("P"):
                continue
            keyword = str(row[4] or "").lower()
            title = str(row[8] or "").lower()
            if any(k in topic_lower for k in keyword.split(", ")) or any(k in topic_lower for k in title.split()):
                return {
                    "id": row[0],
                    "keyword": row[4],
                    "product": row[6],
                    "title": row[8],
                    "image_prompt": row[17] or "",
                    "affiliate": row[15] or "",
                }
    except Exception as e:
        logger.debug(f"No pin match for: {topic} ({e})")
    return {}
