"""Image pipeline — pin images from package first, 9Router ModeImage fallback."""
import os
import re
import json
import random
import urllib.parse
import logging
import base64
import requests
from io import BytesIO
from PIL import Image

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


def _modeimage_url(prompt: str, seed: int = None) -> str:
    """Generate image via Qwen Dashscope SDK. Returns local file path."""
    api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    if not api_key:
        logger.warning("DASHSCOPE_API_KEY not set, skipping image generation")
        return ""

    clean = re.sub(r"<[^>]+>", "", prompt).strip()
    if seed is None:
        seed = random.randint(1, 99999)

    try:
        import dashscope
        dashscope.api_key = api_key
        dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"
        from dashscope import ImageSynthesis
        resp = ImageSynthesis.call(
            model="qwen-image-3.0",
            prompt=clean,
            size="1024*1024",
            n=1,
            seed=seed
        )
        if resp.status_code != 200:
            logger.warning(f"Dashscope error {resp.status_code}: {resp.message}")
            return ""
        
        result = resp.output.results[0]
        if hasattr(result, "url") and result.url:
            img_resp = requests.get(result.url, timeout=30)
            img_bytes = img_resp.content
        elif hasattr(result, "b64_json") and result.b64_json:
            img_bytes = base64.b64decode(result.b64_json)
        else:
            logger.warning("Dashscope: no image in response")
            return ""
        
        cache_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "images")
        os.makedirs(cache_dir, exist_ok=True)
        fpath = os.path.join(cache_dir, f"dashscope_{seed}.jpg")
        img = Image.open(BytesIO(img_bytes))
        if img.mode == "RGBA":
            img = img.convert("RGB")
        img.save(fpath, "JPEG", quality=90)
        logger.info(f"Dashscope image saved: {fpath}")
        return fpath
    except Exception as e:
        logger.warning(f"Dashscope failed: {e}")
        return ""


def resolve_images(article, topic: str, pin_data: dict = None) -> list:
    """Resolve images: pin package first, then 9Router ModeImage fallback."""
    images = []
    
    # Priority 1: Pin package images (match by keyword)
    pin = _match_pin(topic)
    if pin.get("url"):
        images.append({"local": pin["url"], "alt": topic})
        logger.info(f"Pin image matched: {pin['url'][:50]}")
    
    # Priority 2: 9Router ModeImage variations
    xlsx_prompt = pin_data.get("image_prompt", "") if pin_data else ""
    base_prompt = xlsx_prompt if xlsx_prompt else f"Close-up of {topic} nails, beauty editorial, glossy finish"
    
    variations = [
        f"{base_prompt}, flat lay, overhead shot, lifestyle",
        f"{base_prompt.replace('close-up', 'macro')}, detail shot, sharp focus",
        f"{base_prompt}, natural lighting, soft focus, elegant",
    ]
    
    for i, v in enumerate(variations[:3]):
        # Generate local Dashscope image (for Pinterest/download)
        local = _modeimage_url(v, seed=random.randint(1, 99999))
        
        # Use Pollinations URL for article HTML (public, accessible)
        clean = re.sub(r"<[^>]+>", "", v).strip()
        encoded = urllib.parse.quote(clean)
        poll_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1000&height=1500&nologo=true"
        
        images.append({"local": poll_url, "alt": f"{topic} — variation {i+1}", "dashscope": local or ""})
    
    return images
