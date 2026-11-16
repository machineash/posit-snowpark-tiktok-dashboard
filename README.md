# posit-snowpark-tiktok-dashboard
A Shiny for Python dashboard, deployed via Snowflake's Snowpark Container Services, built on real TikTok engagement data (285K followers, up to 2,000 most recent videos).

Built to get hands-on with Snowflake and Snowpark Container Services, and to work with a real Posit product (Shiny for Python) end to end.

## Architecture

```text
TikTok Display API v2 (ingest/oauth_export.py, OAuth 2.0 + PKCE)
  │  JSON export (videos.json, gitignored)
  ▼
Snowflake: tiktok_raw (raw API payload)
  │  SQL transform
  ▼
Snowflake: tiktok_videos (14 cols, analysis-ready)
  │
  v
Shiny for Python dashboard (app.py) ──▶ Docker container ──▶ Snowpark Container Services
```

`db.py` reads Snowflake credentials from environment variables the same way in all three of: local `.env` (Phase 2), plain `docker run`, and the deployed Snowpark Container Services service (Phase 3, credentials as Snowflake Secrets) — no code branches on where it's running.

## Status

- [x] **Phase 1 — data pipeline**: TikTok video data (views, likes, comments, shares, post date) collected via the official Display API and loaded into Snowflake; transformed into `tiktok_videos`.
- [x] **Phase 2 — dashboard**: Shiny for Python app (`app.py`) visualizing engagement trends, top posts, organic vs. sponsored performance, and duration vs. performance — querying Snowflake live via `db.py`.
- [x] **Phase 3 — deploy**: `Dockerfile` + `deploy/` scripts for image repository, compute pool, secrets, service spec, and service creation on Snowpark Container Services. See "Deployment" below.
- [-] **Phase 4 — docs**: architecture diagram, partner-style deployment writeup.

## Data ingestion (`/ingest`)

Self-serve OAuth 2.0 (PKCE) exporter built against the official TikTok Display API (`/v2/video/list/`).

| File | What it does |
| :--- | :--- |
| `ingest/oauth_export.py` | Local Flask server that handles TikTok OAuth login (`user.info.basic`, `video.list`) and paginates up to 2,000 recent videos into `ingest/videos.json` |

### Exporting your own TikTok data locally

1. Create a Desktop app in the TikTok Developer Portal, enable **Login Kit** and **Display API**, and register `http://localhost:3000/callback` as your Redirect URI.
2. Copy `.env.example` to `.env` and add your `TIKTOK_CLIENT_KEY` and `TIKTOK_CLIENT_SECRET`.
3. Install dependencies and run the exporter:
   ```bash
   pip install flask requests python-dotenv
   python ingest/oauth_export.py
   ```
4. Open `http://localhost:3000` in your browser and authorize your account. Your tokens (`tokens.json`) and video export (`videos.json`) are saved locally inside `ingest/` and excluded from Git via `.gitignore`.

## Data pipeline (`/sql`)

| File | What it does |
| :--- | :--- |
| `01_create_tables.sql` | Creates `tiktok_raw` (raw schema) and `tiktok_videos` (clean, analysis-ready schema) |
| `02_load_raw.sql` | File format and load notes for getting the exported data into `tiktok_raw` |
| `03_transform_to_clean.sql` | Transforms `tiktok_raw` into `tiktok_videos` |

## Dashboard (`app.py`)

Shiny for Python app, connecting live to Snowflake (no local data copy).

- **Engagement over time** — weekly views/likes/comments/shares trend
- **Top posts** — `video_id`, `post_date`, and metrics only (no `caption`, no `cover_url` — excluded at the SQL query level in `db.py`, never pulled into the app)
- **Organic vs. sponsored** — average metrics split by `is_sponsored` / `is_ad`
- **Duration vs. performance** — avg. views binned by `duration_secs`
- **Sidebar filters** — date range, sponsored/organic toggle

### Running it locally

```bash
pip install -r requirements.txt
cp .env.example .env
# fill in your Snowflake credentials
shiny run app.py
```

Credentials are read from environment variables (via `python-dotenv` in dev); `db.py` will need no changes when Phase 3 sets them as container secrets instead.

**Known issue:** live queries and filters are confirmed working end to end against real Snowflake data, but chart card sizing still needs a polish pass — plots render slightly cramped in some viewport sizes. Functionality isn't affected; tracked as an open follow-up.

## Deployment (`/deploy`)

Containerized and deployed to Snowpark Container Services, plus what to check if the service doesn't start.

| File | What it does |
| :--- | :--- |
| `Dockerfile` | Builds the dashboard image; runs `shiny run app.py` on port 8000 |
| `deploy/01_image_repository.sql` | Creates the Snowflake image repository |
| `deploy/02_compute_pool.sql` | Creates the compute pool the service runs on |
| `deploy/03_secrets.sql` | Stores Snowflake credentials as Secrets (no password in the image) |
| `deploy/service_spec.yaml` | Container spec: image, env vars, injected secrets, exposed port |
| `deploy/04_create_service.sql` | Stages the spec and creates/checks the running service |

## Data source

TikTok video metadata and engagement metrics collected via the official TikTok Display API (`/v2/video/list/`), covering up to 2,000 recent videos from my personal account. Fields used: view, like, comment, and share counts, post timestamp, video duration, and video ID. Raw exports remain local (`ingest/videos.json`) and are never committed to the repository.


