"""Image pipeline — pin images from package first, Pollinations fallback."""
import os
import re
import json
import random
import urllib.parse
import logging

logger = logging.getLogger("engine.image")

# Load pin image mapping
PIN_IMAGES = {}
_config_dir = os.path.join(os.path.dirname(__file__), "..", "..", "config")
_pin_file = os.path.join(_config_dir, "pin_images.json")
if os.path.exists(_pin_file):
    PIN_IMAGES = json.load(open(_pin_file))


def _match_pin(topic: str) -> dict:
    """Match topic to best pin image by keyword overlap."""
    topic_lower = topic.lower()
    best_score = 0
    best_pin = None
    for pin_id, data in PIN_IMAGES.items():
        score = sum(1 for kw in data["keywords"] if kw.lower() in topic_lower)
        if score > best_score:
            best_score = score
            best_pin = data
    return best_pin or {}


def load_pin_data(xlsx_path: str, topic: str) -> dict:
    """Match topic to pin data from master xlsx for image prompts."""
    try:
        import openpyxl
        wb = openpyxl.load_workbook(xlsx_path)
        ws = wb["Pin_Content_60"]
        topic_lower = topic.lower()
        for row in ws.iter_rows(values_only=True):
            if not row[0] or not str(row[0]).startswith("P"): continue
            keyword = str(row[4] or "").lower()
            title = str(row[8] or "").lower()
            if any(k in topic_lower for k in keyword.split(", ")) or any(k in topic_lower for k in title.split()):
                return {"id": row[0], "keyword": row[4], "product": row[6], "title": row[8], "image_prompt": row[17] or "", "affiliate": row[15] or ""}
    except Exception: pass
    return {}


def _pollinations_url(prompt: str, width=1000, height=1500) -> str:
    """Generate Pollinations URL as fallback."""
    clean = re.sub(r"<[^>]+>", "", prompt).strip()
    encoded = urllib.parse.quote(clean)
    return f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true"


def resolve_images(article, topic: str, pin_data: dict = None) -> list:
    """Resolve images: pin package first, then Pollinations fallback."""
    images = []
    
    # Priority 1: Pin package images (match by keyword)
    pin = _match_pin(topic)
    if pin.get("url"):
        images.append({"local": pin["url"], "alt": topic})
        logger.info(f"Pin image matched: {pin['url'][:50]}")
    
    # Priority 2: Pollinations variations for variety
    xlsx_prompt = pin_data.get("image_prompt", "") if pin_data else ""
    base_prompt = xlsx_prompt if xlsx_prompt else f"Close-up of {topic} nails, beauty editorial, glossy finish"
    
    variations = [
        f"{base_prompt}, flat lay, overhead shot, lifestyle",
        f"{base_prompt.replace('close-up', 'macro')}, detail shot, sharp focus",
        f"{base_prompt}, natural lighting, soft focus, elegant",
        f"{base_prompt}, both hands, symmetrical, studio lighting",
    ]
    
    for i, v in enumerate(variations[:3]):
        images.append({"local": _pollinations_url(v), "alt": f"{topic} — variation {i+1}"})
    
    return images
