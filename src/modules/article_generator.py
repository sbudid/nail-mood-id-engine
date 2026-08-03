"""Step 3: Article Generation via 9Router Mode3."""
from dataclasses import dataclass, field
from typing import List
import re
import requests
import os
from src.modules.keyword_research import SEOPlan, ROUTER_URL, ROUTER_KEY


@dataclass
class Article:
    title: str
    content_html: str
    meta_description: str
    required_images: List[dict] = field(default_factory=list)
    faq_items: List[dict] = field(default_factory=list)
    shopee_links: List[dict] = field(default_factory=list)


class ArticleWriter:
    def write(self, seo_plan: SEOPlan, word_count: tuple = (1500, 2500)) -> Article:
        prompt = f"""Tulis artikel panjang (1500-2000 kata) tentang "{seo_plan.primary_keyword}" dalam Bahasa Indonesia.

Gaya: natural, ramah, seperti teman yang berbagi tips tentang kuku. Bukan gaya dokter atau akademik.

Struktur wajib:
1. H2 heading untuk setiap bagian utama (minimal 5 bagian)
2. Sertakan tips praktis yang bisa langsung dipraktikkan
3. FAQ section di akhir dengan tepat 5 pertanyaan (H3 headings)
4. Kesimpulan di akhir sebelum FAQ

HTML format:
- Pakai <h2> untuk judul bagian
- <p> untuk paragraf
- <ul><li> untuk list tips
- <strong> hanya untuk penekanan个别 kata, jang wrap seluruh paragraf
- <em> untuk catatan/disclaimer
- JANGAN pakai <h1>

Disclaimer di akhir (sebelum FAQ):
<p><em>Catatan: Konten ini bersifat edukasi umum, bukan pengganti konsultasi profesional.</em></p>

JANGAN sertakan "ditulis oleh" atau atribusi penulis.
JANGAN pakai code block atau markdown — HTML murni."""

        try:
            resp = requests.post(ROUTER_URL, json={
                "model": "Mode3",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 8000,
                "temperature": 0.7,
                "stream": False
            }, headers={"Authorization": f"Bearer {ROUTER_KEY}", "Content-Type": "application/json"}, timeout=300)
            
            data = resp.json()
            msg = data["choices"][0]["message"]
            content = msg.get("content") or msg.get("reasoning") or ""
            
            # Clean markdown fences
            content = re.sub(r'```html\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            
            # Extract title from first non-faq H2
            skip = ['pertanyaan yang sering', 'kesimpulan', 'faq']
            h2s = re.findall(r'<h2[^>]*>([^<]+)</h2>', content)
            title = seo_plan.primary_keyword.title()
            for h in h2s:
                if not any(s in h.lower() for s in skip):
                    title = h.strip()
                    break
            
            # Build meta description
            first_p = re.search(r'<p[^>]*>([^<]+)</p>', content)
            meta = first_p.group(1)[:155] if first_p else f"Panduan lengkap {seo_plan.primary_keyword} untuk pemula."
            
            # Validate word count
            clean_text = re.sub(r'<[^>]+>', '', content)
            wc = len(clean_text.split())
            print(f"  Words: {wc}, H2: {len(re.findall(r'<h2', content))}")
            
            return Article(
                title=title[:120],
                content_html=content,
                meta_description=meta,
            )
        except Exception as e:
            print(f"  Article gen error: {e}")
            return Article(title="Error", content_html="<p>Generation failed</p>", meta_description="")
