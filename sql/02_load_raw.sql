-- Phase 1: load ingest/videos.json into tiktok_raw
USE DATABASE TIKTOK_DASHBOARD;
USE SCHEMA PUBLIC;

CREATE OR REPLACE FILE FORMAT tiktok_json_format
    TYPE = 'JSON'
    STRIP_OUTER_ARRAY = TRUE;

CREATE OR REPLACE STAGE tiktok_ingest_stage
    FILE_FORMAT = tiktok_json_format;

-- Run via SnowSQL or Snowflake CLI from the repo root:
-- PUT file://ingest/videos.json @tiktok_ingest_stage AUTO_COMPRESS=TRUE OVERWRITE=TRUE;

COPY INTO "TIKTOK_DASHBOARD"."PUBLIC"."tiktok_raw" (raw_data)
FROM @tiktok_ingest_stage/videos.json.gz
FILE_FORMAT = (FORMAT_NAME = tiktok_json_format);
