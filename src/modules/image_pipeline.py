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
    """Generate image via Qwen Dashscope API. Returns local file path."""
    api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    if not api_key:
        logger.warning("DASHSCOPE_API_KEY not set, skipping image generation")
        return ""

    clean = re.sub(r"<[^>]+>", "", prompt).strip()
    if seed is None:
        seed = random.randint(1, 99999)

    try:
        # Submit async task
        resp = requests.post(
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json", "X-DashScope-Async": "enable"},
            json={"model": "wanx2.1-t2i-turbo", "input": {"prompt": clean}, "parameters": {"size": "1024*1024", "n": 1}},
            timeout=30
        )
        if resp.status_code != 200:
            logger.warning(f"Dashscope submit error {resp.status_code}: {resp.text[:200]}")
            return ""
        
        task_id = resp.json().get("output", {}).get("task_id", "")
        if not task_id:
            logger.warning(f"No task_id: {resp.text[:200]}")
            return ""
        
        # Poll for result (max 90s)
        for _ in range(30):
            time.sleep(3)
            poll = requests.get(
                f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=15
            )
            status = poll.json().get("output", {}).get("task_status", "")
            if status == "SUCCEEDED":
                results = poll.json()["output"].get("results", [{}])
                img_url = results[0].get("url", "") if results else ""
                if not img_url:
                    logger.warning("Dashscope: no image URL in result")
                    return ""
                img_resp = requests.get(img_url, timeout=30)
                img_bytes = img_resp.content
                cache_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "images")
                os.makedirs(cache_dir, exist_ok=True)
                fpath = os.path.join(cache_dir, f"dashscope_{seed}.jpg")
                img = Image.open(BytesIO(img_bytes))
                if img.mode == "RGBA":
                    img = img.convert("RGB")
                img.save(fpath, "JPEG", quality=90)
                logger.info(f"Dashscope image saved: {fpath}")
                return fpath
            elif status == "FAILED":
                logger.warning(f"Dashscope task failed: {poll.text[:200]}")
                return ""
        
        logger.warning("Dashscope task timed out")
        return ""
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
        # Try 9Router ModeImage first
        local = _modeimage_url(v, seed=random.randint(1, 99999))
        if local:
            images.append({"local": local, "alt": f"{topic} — variation {i+1}"})
            continue
        # Fallback: Pollinations URL
        clean = re.sub(r"<[^>]+>", "", v).strip()
        encoded = urllib.parse.quote(clean)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1000&height=1500&nologo=true"
        images.append({"local": url, "alt": f"{topic} — variation {i+1}"})
    
    return images
