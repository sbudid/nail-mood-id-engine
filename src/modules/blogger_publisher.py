"""Step 9 & 10: Blogger Publisher via API."""
import os
import sys
import json
import requests
import datetime

sys.path.insert(0, "/home/ubuntu/autoblog-bumil")
from auto_blog import get_blogger_token


class BloggerPublisher:
    def __init__(self, blog_id: str = ""):
        self.blog_id = blog_id or os.getenv("BLOGGER_BLOG_ID", "4276182482507605794")

    def publish(self, article, labels: list = None) -> dict:
        """Publish article to Blogger. Returns post info."""
        token = get_blogger_token()
        
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
            return {"success": False, "error": resp.text[:200]}
