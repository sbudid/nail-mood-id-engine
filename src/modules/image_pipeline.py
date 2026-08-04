"""Image pipeline — uses Pollinations.ai (free) with prompts from master xlsx."""
import os
import re
import urllib.parse
import urllib.request
import logging

logger = logging.getLogger("engine.image")


def generate_image(prompt: str, save_path: str, width: int = 1000, height: int = 1500) -> str:
    """Generate image via Pollinations.ai. Returns local path."""
    clean_prompt = re.sub(r"<[^>]+>", "", prompt).strip()
    if len(clean_prompt) < 10:
        clean_prompt = "beautiful nail art, close up, elegant, glossy finish, clean background"

    encoded = urllib.parse.quote(clean_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&seed=42"

    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        urllib.request.urlretrieve(url, save_path)
        size = os.path.getsize(save_path)
        if size > 5000:
            logger.info(f"Image generated: {size/1024:.0f}KB")
            return save_path
        else:
            logger.warning(f"Image too small: {size}B")
            return ""
    except Exception as e:
        logger.error(f"Image gen failed: {e}")
        return ""


def resolve_images(article, topic: str, pin_data: dict = None) -> list:
    """Resolve images: Pollinations AI using prompts from xlsx or fallback."""
    images = []
    save_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "Images")
    os.makedirs(save_dir, exist_ok=True)

    # Get prompt from pin_data if available
    prompt = pin_data.get("image_prompt", "") if pin_data else ""
    if not prompt:
        prompt = f"Vertical Pinterest beauty editorial, 2:3. Close-up of {topic} nails, realistic, glossy finish, clean background, elegant, beauty editorial style"

    # Generate 1 main image
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower())[:40]
    main_path = os.path.join(save_dir, f"{slug}_main.jpg")
    result = generate_image(prompt, main_path)
    if result:
        images.append({"local": result, "alt": topic})

    # Generate 1 supporting image with varied prompt
    support_prompt = prompt.replace("close-up", "flat lay").replace("editorial", "lifestyle") + ", different angle, natural lighting"
    support_path = os.path.join(save_dir, f"{slug}_support.jpg")
    result2 = generate_image(support_prompt, support_path)
    if result2:
        images.append({"local": result2, "alt": f"{topic} overview"})

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
