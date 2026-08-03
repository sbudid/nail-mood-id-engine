# Nail Mood ID Engine — Master Specification

## Overview
Modular Automation Engine untuk konten blog + Pinterest di niche kuku (nails).
Dirancang agar mudah di-port ke niche lain (hijab, skincare, dll) tanpa ubah kode.

## Pipeline Steps
1. **Keyword Research** — generate keyword plan dari topic
2. **SEO Planning** — primary, secondary, long-tail keywords
3. **Article Generation** — tulis article 1500-2500 kata, EEAT-compliant
4. **Image Pipeline** — resolve gambar: Existing > Stock > Shopee > AI (token-optimized)
5. **Pinterest Pins** — generate pin metadata + image
6. **Shopee Affiliates** — generate affiliate links + disclaimer
7. **SEO Enhancement** — FAQ schema, meta tags, structured data
8. **HTML Builder** — generate Blogger-compatible HTML
9. **Export** — save ke data/Published/
10. **Publish** — manual atau via GitHub Actions

## Token Optimization
Image resolution priority (wajib):
1. **Existing** — cek data/Images/existing/ dulu
2. **Free Stock** — Unsplash/Pexels API (gratis)
3. **Shopee** — product image dari affiliate
4. **AI Generated** — LAST RESORT ONLY (biaya token)

## Pinterest Safety
- Destination URL selalu article slug, bukan link affiliate langsung
- Max 2 pins per article

## Shopee Compliance
- Disclaimer otomatis di setiap artikel yang mengandung affiliate
- Disclaimer text: lihat config/settings.yaml

## Scalability
Untuk niche baru:
1. Duplikasi `config/settings.yaml` → ganti nama, keywords, url
2. Duplikasi `config/categories.yaml` → ganti kategori
3. Jalankan: `python -m src.core.orchestrator --topic "Topik Baru"`

## Platform Ports
- Blogger: sudah built-in (default)
- WordPress: tambah `src/modules/wordpress_publisher.py`
- Ghost: tambah `src/modules/ghost_publisher.py`
