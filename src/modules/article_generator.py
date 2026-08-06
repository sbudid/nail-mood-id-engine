"""Step 3: Article Generation via 9Router Mode3 — with images + affiliate."""
from dataclasses import dataclass, field
from typing import List
import re
import requests
import os
from src.modules.keyword_research import SEOPlan, ROUTER_URL, ROUTER_KEY

# Shopee affiliate links — REAL from NailMoodID_Master_60Pins.xlsx
AFFILIATE_LINKS = {
    "gel polish set": "https://s.shopee.co.id/7AcNpx69T8",
    "beginner gel nails": "https://s.shopee.co.id/7AcNpx69T8",
    "nude nails": "https://s.shopee.co.id/70Ixde6mo7",
    "clean girl nails": "https://s.shopee.co.id/70Ixde6mo7",
    "uv nail lamp": "https://s.shopee.co.id/7VFEEZ4snE",
    "wedding nails": "https://s.shopee.co.id/5LAjeaD8Bt",
    "press on nails": "https://s.shopee.co.id/6L3GqQ9KAB",
    "glass cat eye": "https://s.shopee.co.id/6Ajqe79xV6",
    "red nails": "https://s.shopee.co.id/4AymGRHZYm",
    "marble wedding": "https://s.shopee.co.id/6VMh2j8gpC",
    "handmade press on": "https://s.shopee.co.id/5q70FVBEB0",
    "korean flower": "https://s.shopee.co.id/5fna3CBrVz",
    "portable nail lamp": "https://s.shopee.co.id/7fYeQs4FSJ",
    "gel nail removal": "https://s.shopee.co.id/40fM48ICtl",
}

# Free stock images per niche
STOCK_IMAGES = {
    "nails": [],
    "gel": [],
    "art": [],
}


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
        # Find matching affiliate link
        affiliate_url = ""
        for key, url in AFFILIATE_LINKS.items():
            if key in seo_plan.primary_keyword.lower():
                affiliate_url = url
                break
        if not affiliate_url:
            affiliate_url = AFFILIATE_LINKS.get("gel polish set", "https://s.shopee.co.id/7AcNpx69T8")

        # Find matching stock images
        images = []
        for key, imgs in STOCK_IMAGES.items():
            if key in seo_plan.primary_keyword.lower():
                images = imgs
                break
        if not images:
            images = STOCK_IMAGES.get("nails", ["https://images.unsplash.com/photo-1604654894610-df63bc536371?w=800"])

        prompt = f"""Tulis artikel panjang (1500-2000 kata) tentang "{seo_plan.primary_keyword}" dalam Bahasa Indonesia.

Gaya: natural, ramah, seperti teman yang berbagi tips tentang kuku. Bukan gaya dokter.

ATURAN PENTING:
1. Setiap <h2> bagian utama HARUS diikuti <img> gambar di baris berikutnya:
   <img src="GAMBAR_URL" alt="DESKRIPSI GAMBAR" width="100%">
   Gunakan URL gambar ini (rotate): {images[0] if images else 'https://images.unsplash.com/photo-1604654894610-df63bc536371?w=800'}

2. Di akhir artikel SEBELUM FAQ, tambahkan section affiliate CTA:
   <h2>Rekomendasi Produk</h2>
   <p>Mau beli produk terkait? Lihat rekomendasi terbaik di Shopee:</p>
   <p style="text-align:center;"><a href="{affiliate_url}" target="_blank" style="background:#FF4500;color:white;padding:12px 24px;text-decoration:none;border-radius:8px;font-size:16px;">🛒 Beli di Shopee Sekarang</a></p>

3. Struktur wajib:
   - <h2> untuk judul bagian (minimal 5)
   - <img> SETIAP H2 (pake URL dari atas)
   - <p> untuk paragraf
   - <ul><li> untuk list tips
   - <strong> untuk penekanan个别 kata saja
   - FAQ 5 pertanyaan (<h3>)
   - Disclaimer di akhir

4. Disclaimer: <p><em>Catatan: Konten ini bersifat edukasi umum, bukan pengganti konsultasi profesional. Link afiliasi di atas membantu kami tetap menghasilkan konten gratis untuk Anda.</em></p>

JANGAN: "ditulis oleh", code block, markdown."""

        try:
            resp = requests.post(ROUTER_URL, json={
                "model": "Mode3",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 8000,
                "temperature": 0.7,
                "stream": False
            }, headers={"Authorization": f"Bearer {ROUTER_KEY}", "Content-Type": "application/json"}, timeout=480)
            
            data = resp.json()
            msg = data["choices"][0]["message"]
            content = msg.get("content") or msg.get("reasoning") or ""
            
            # Clean markdown fences
            content = re.sub(r'```html\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            
            # --- HTML post-processing ---
            # Fix orphan <strong> inside lists: wrap bare <strong>text</strong> lines in <li>
            content = re.sub(r'(?<=\n)\s*<strong>([^<]+)</strong>([^<]*)</strong>\s*(?=\n|$)', r'<li><strong>\1</strong>\2</li>', content)
            
            # Fix broken list items: <li> with only <strong> — add missing text before
            content = re.sub(r'<li>\s*<strong>([^<]+)</strong>\s*</li>', r'<li><strong>\1</strong></li>', content)
            
            # Wrap consecutive <li> in <ul> if not already
            li_block = re.findall(r'(<li>.*?</li>(\s*\n)*)+', content)
            for block in li_block:
                if not block.strip().startswith('<ul>'):
                    ul = '<ul>' + block.strip() + '</ul>'
                    content = content.replace(block.strip(), ul, 1)
            
            # Ensure paragraphs: text between tags not in <p> gets wrapped
            parts = re.split(r'(</?h[23][^>]*>|<img[^>]*>|<ul[^>]*>|</ul>|<li[^>]*>|</li>)', content)
            result = []
            in_list = False
            for part in parts:
                if re.match(r'<ul', part):
                    in_list = True
                    result.append(part)
                elif part == '</ul>':
                    in_list = False
                    result.append(part)
                elif re.match(r'<li', part) or part == '</li>' or re.match(r'</?h[23]', part) or re.match(r'<img', part):
                    result.append(part)
                elif part.strip() and not in_list:
                    stripped = part.strip()
                    if stripped and not stripped.startswith('<p>') and not stripped.startswith('<strong>'):
                        result.append(f'<p>{stripped}</p>')
                    else:
                        result.append(part)
                else:
                    result.append(part)
            content = ''.join(result)
            
            # If no images in output, inject after first <h2>
            if '<img' not in content:
                first_h2 = re.search(r'(</h2>)', content)
                if first_h2:
                    img_tag = f'\n<img src="{images[0]}" alt="{seo_plan.primary_keyword}" width="100%">'
                    content = content[:first_h2.end()] + img_tag + content[first_h2.end():]
            
            # Extract title
            skip = ['pertanyaan yang sering', 'kesimpulan', 'faq']
            h2s = re.findall(r'<h2[^>]*>([^<]+)</h2>', content)
            title = seo_plan.primary_keyword.title()
            for h in h2s:
                if not any(s in h.lower() for s in skip):
                    title = h.strip()
                    break
            
            first_p = re.search(r'<p[^>]*>([^<]+)</p>', content)
            meta = first_p.group(1)[:155] if first_p else f"Panduan {seo_plan.primary_keyword}."
            
            wc = len(re.sub(r'<[^>]+>', '', content).split())
            img_count = len(re.findall(r'<img', content))
            print(f"  Words: {wc}, H2: {len(re.findall(r'<h2', content))}, Images: {img_count}, Affiliate: {'affiliate' in content.lower() or 'shopee' in content.lower()}")
            
            return Article(
                title=title[:120],
                content_html=content,
                meta_description=meta,
            )
        except Exception as e:
            print(f"  Article gen error: {e}")
            return Article(title="Error", content_html="", meta_description="")
