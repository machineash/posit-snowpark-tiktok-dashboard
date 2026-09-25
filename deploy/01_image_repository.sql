-- Phase 3, step 1: image repository
-- Snowflake needs somewhere inside your account to store the Docker image
-- before a compute pool can run it. One repo per project is plenty.

CREATE IMAGE REPOSITORY IF NOT EXISTS "TIKTOK_DASHBOARD"."PUBLIC".tiktok_dashboard_repo;

-- Grab the repository_url from here — you'll docker tag/push to it.
SHOW IMAGE REPOSITORIES IN SCHEMA "TIKTOK_DASHBOARD"."PUBLIC";
