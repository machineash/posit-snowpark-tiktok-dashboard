-- Phase 1: schema setup (Official TikTok Display API v2 JSON schema)
-- Database/schema: TIKTOK_DASHBOARD.PUBLIC

CREATE OR REPLACE TABLE "TIKTOK_DASHBOARD"."PUBLIC"."tiktok_raw" (
    loaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    raw_data  VARIANT
);

-- Clean, analysis-ready table the dashboard queries (unchanged for db.py / app.py)
CREATE OR REPLACE TABLE "TIKTOK_DASHBOARD"."PUBLIC"."tiktok_videos" (
    video_id       VARCHAR,
    video_url      VARCHAR,
    caption        VARCHAR,
    cover_url      VARCHAR,
    post_date      TIMESTAMP_NTZ,
    views          NUMBER,
    likes          NUMBER,
    comments       NUMBER,
    shares         NUMBER,
    saves          NUMBER,
    duration_secs  NUMBER,
    is_sponsored   BOOLEAN,
    is_ad          BOOLEAN,
    is_pinned      BOOLEAN
);
