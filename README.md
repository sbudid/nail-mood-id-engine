# Nail Mood ID Engine

Modular Automation Engine untuk konten blog + Pinterest di niche kuku (nails).

## Quick Start
```bash
pip install -r requirements.txt
python -m src.core.orchestrator --topic "Gel Nails"
```

## Structure
```
src/
  core/orchestrator.py     # Pipeline utama
  core/token_optimizer.py  # Image priority resolver
  modules/                 # Keyword, Article, Pinterest, Shopee, SEO
  utils/                   # Logger, file I/O
config/                    # settings.yaml, categories.yaml
templates/                 # HTML & JSON templates
data/                      # Output (gitignored)
```

## Image Priority (Token-Safe)
1. Existing assets → 2. Free stock → 3. Shopee images → 4. AI generation (last resort)

## GitHub Actions
Trigger via `workflow_dispatch` — masukkan topic, jalankan pipeline.

## License
MIT
