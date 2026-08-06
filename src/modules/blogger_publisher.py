"""Step 9 & 10: Blogger Publisher via API."""
import os
import sys
import json
import requests
import datetime
import logging

logger = logging.getLogger("engine.publish")


def _get_blogger_token():
    """Get Blogger access token from env vars or fallback to local file."""
    refresh_token = os.getenv("BLOGGER_REFRESH_TOKEN")
    client_id = os.getenv("BLOGGER_CLIENT_ID", "651496957848-t0ik8spuggutsp4k2thjk9o8a1sk900b.apps.googleusercontent.com")
    client_secret = os.getenv("BLOGGER_CLIENT_SECRET", "")
    
    if refresh_token and client_secret:
        resp = requests.post("https://oauth2.googleapis.com/token", data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        })
        return resp.json().get("access_token", "")
    
    # Fallback: import from autoblog-bumil
    try:
        sys.path.insert(0, "/home/ubuntu/autoblog-bumil")
        from auto_blog import get_blogger_token
        return get_blogger_token()
    except Exception:
        return ""


class BloggerPublisher:
    def __init__(self, blog_id: str = ""):
        self.blog_id = blog_id or os.getenv("BLOGGER_BLOG_ID", "4276182482507605794")

    def publish(self, article, labels: list = None) -> dict:
        """Publish article to Blogger. Returns post info."""
        token = _get_blogger_token()
        
        post = {
            "kind": "blogger#post",
            "blog": {"id": self.blog_id},
            "title": article.title,
            "content": article.content_html,
            "labels": labels or ["Nail Art", "Tips Kuku"],
            "status": "LIVE",
        }
        
        resp = requests.post(
            f"https://www.googleapis.com/blogger/v3/blogs/{self.blog_id}/posts",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=post,
            timeout=30,
        )
        
        if resp.status_code == 200:
            data = resp.json()
            return {"success": True, "id": data["id"], "url": data["url"]}
        else:
            logger.error(f"Blogger publish failed {resp.status_code}: {resp.text[:300]}")
            return {"success": False, "error": resp.text[:200]}
