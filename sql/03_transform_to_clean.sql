-- Phase 1: transform tiktok_raw (114 columns, straight from the scraper)
-- into tiktok_videos (14 columns, what the dashboard actually queries).

INSERT INTO "TIKTOK_DASHBOARD"."PUBLIC".tiktok_videos
SELECT
    id::VARCHAR           AS video_id,
    webVideoUrl           AS video_url,
    text                  AS caption,
    createTimeISO         AS post_date,
    playCount             AS views,
    diggCount             AS likes,
    commentCount          AS comments,
    shareCount            AS shares,
    collectCount          AS saves,
    "videoMeta/duration"  AS duration_secs,
    "videoMeta/coverUrl"  AS cover_url,
    isSponsored           AS is_sponsored,
    isAd                  AS is_ad,
    isPinned              AS is_pinned
FROM "TIKTOK_DASHBOARD"."PUBLIC"."tiktok_raw";

-- Sanity check
SELECT video_id, post_date, views, likes, comments, shares, saves
FROM "TIKTOK_DASHBOARD"."PUBLIC".tiktok_videos
ORDER BY post_date DESC
LIMIT 5;
