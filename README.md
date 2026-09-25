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

`db.py` reads Snowflake credentials from environment variables the same
way in all three of: local `.env` (Phase 2), plain `docker run`, and the
deployed Snowpark Container Services service (Phase 3, credentials as
Snowflake Secrets) — no code branches on where it's running.

## Status

- [x] **Phase 1 — data pipeline**: TikTok video data (views, likes, comments,
      shares, saves, post date) scraped and loaded into Snowflake;
      1,000 rows in `tiktok_videos`.
- [x] **Phase 2 — dashboard**: Shiny for Python app (`app.py`) visualizing
      engagement trends, top posts, organic vs. sponsored performance, and
      duration vs. performance — querying Snowflake live via `db.py`.
- [x] **Phase 3 — deploy**: `Dockerfile` + `deploy/` scripts for image
      repository, compute pool, secrets, service spec, and service
      creation on Snowpark Container Services. See "Deployment" below.
- [ ] **Phase 4 — docs**: architecture diagram, partner-style deployment
      writeup.

## Data pipeline (`/sql`)

| File | What it does |
|---|---|
| `01_create_tables.sql` | Creates `tiktok_raw` (raw scraper schema) and `tiktok_videos` (clean, analysis-ready schema) |
| `02_load_raw.sql` | File format + load notes for getting the scraped CSV into `tiktok_raw` |
| `03_transform_to_clean.sql` | Transforms `tiktok_raw` → `tiktok_videos` |

## Dashboard (`app.py`)

Shiny for Python app, connecting live to Snowflake (no local data copy).

- **Engagement over time** — weekly views/likes/comments/shares/saves trend
- **Top posts** — `video_id`, `post_date`, and metrics only (no `caption`,
  no `cover_url` — excluded at the SQL query level in `db.py`, never
  pulled into the app)
- **Organic vs. sponsored** — average metrics split by `is_sponsored`/`is_ad`
- **Duration vs. performance** — avg. views binned by `duration_secs`
- **Sidebar filters** — date range, sponsored/organic toggle

### Running it locally

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your Snowflake credentials
shiny run app.py
```

Credentials are read from environment variables (via `python-dotenv` in
dev); `db.py` will need no changes when Phase 3 sets them as container
secrets instead.

**Known issue:** live queries and filters are confirmed working end to
end against real Snowflake data, but chart card sizing still needs a
polish pass — plots render slightly cramped in some viewport sizes.
Functionality isn't affected; tracked as an open follow-up.

## Deployment (`/deploy`)

Containerized and deployed to Snowpark Container Services — see
`deploy/README.md` for the full walkthrough (image repository, compute
pool, credentials as Snowflake Secrets, service spec, and bringing the
service up), plus what to check if the service doesn't start.

| File | What it does |
|---|---|
| `Dockerfile` | Builds the dashboard image; runs `shiny run app.py` on port 8000 |
| `deploy/01_image_repository.sql` | Creates the Snowflake image repository |
| `deploy/02_compute_pool.sql` | Creates the compute pool the service runs on |
| `deploy/03_secrets.sql` | Stores Snowflake credentials as Secrets (no password in the image) |
| `deploy/service_spec.yaml` | Container spec: image, env vars, injected secrets, exposed port |
| `deploy/04_create_service.sql` | Stages the spec and creates/checks the running service |

## Data source

TikTok video data collected via [Apify's TikTok
Scraper](https://apify.com/clockworks/tiktok-scraper) (profile export mode),
covering the 1,000 most recent videos from my own account as of
September 2026. Fields used: view/like/comment/share/save counts, post
date, video URL, cover image, and sponsored/ad/pinned flags.
