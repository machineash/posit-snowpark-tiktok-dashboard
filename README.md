# posit-snowpark-tiktok-dashboard

A Shiny for Python dashboard, deployed via Snowflake's Snowpark Container
Services, built on my own TikTok account's real engagement data (285K
followers, 1,000 most recent videos).

Built to get hands-on with Snowflake and Snowpark Container Services, and
to work with a real Posit product (Shiny for Python) end to end.

## Architecture

```
TikTok scraper (Apify clockworks/tiktok-scraper)
        │  CSV export
        ▼
Snowflake: tiktok_raw          (114 cols, raw scraper output)
        │  SQL transform
        ▼
Snowflake: tiktok_videos       (14 cols, analysis-ready)
        │
        ▼
Shiny for Python dashboard  ──▶  Docker container  ──▶  Snowpark Container Services
```

## Status

- [x] **Phase 1 — data pipeline**: TikTok video data (views, likes, comments,
      shares, saves, post date) scraped and loaded into Snowflake;
      1,000 rows in `tiktok_videos`.
- [ ] **Phase 2 — dashboard**: Shiny for Python app visualizing engagement
      trends, top posts, and organic vs. sponsored performance.
- [ ] **Phase 3 — deploy**: containerize and deploy via Snowpark Container
      Services (compute pool, external access integration).
- [ ] **Phase 4 — docs**: architecture diagram, partner-style deployment
      writeup.

## Data pipeline (`/sql`)

| File | What it does |
|---|---|
| `01_create_tables.sql` | Creates `tiktok_raw` (raw scraper schema) and `tiktok_videos` (clean, analysis-ready schema) |
| `02_load_raw.sql` | File format + load notes for getting the scraped CSV into `tiktok_raw` |
| `03_transform_to_clean.sql` | Transforms `tiktok_raw` → `tiktok_videos` |

## Data source

TikTok video data collected via [Apify's TikTok
Scraper](https://apify.com/clockworks/tiktok-scraper) (profile export mode),
covering the 1,000 most recent videos from my own account as of
September 2026. Fields used: view/like/comment/share/save counts, post
date, video URL, cover image, and sponsored/ad/pinned flags.
