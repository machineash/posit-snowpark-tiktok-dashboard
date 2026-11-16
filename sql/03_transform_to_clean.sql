-- Phase 1: transform JSON VARIANT rows -> analysis-ready tiktok_videos
TRUNCATE TABLE "TIKTOK_DASHBOARD"."PUBLIC"."tiktok_videos";

INSERT INTO "TIKTOK_DASHBOARD"."PUBLIC"."tiktok_videos" (
    video_id,
    video_url,
    caption,
    cover_url,
    post_date,
    views,
    likes,
    comments,
    shares,
    saves,
    duration_secs,
    is_sponsored,
    is_ad,
    is_pinned
)
SELECT
    raw_data:id::VARCHAR                                           AS video_id,
    raw_data:share_url::VARCHAR                                    AS video_url,
    COALESCE(raw_data:video_description::VARCHAR, raw_data:title::VARCHAR) AS caption,
    raw_data:cover_image_url::VARCHAR                              AS cover_url,
    TO_TIMESTAMP_NTZ(raw_data:create_time::NUMBER)                 AS post_date,
    COALESCE(raw_data:view_count::NUMBER, 0)                       AS views,
    COALESCE(raw_data:like_count::NUMBER, 0)                       AS likes,
    COALESCE(raw_data:comment_count::NUMBER, 0)                    AS comments,
    COALESCE(raw_data:share_count::NUMBER, 0)                      AS shares,
    0                                                              AS saves,
    COALESCE(raw_data:duration::NUMBER, 0)                         AS duration_secs,
    REGEXP_LIKE(
        COALESCE(raw_data:video_description::VARCHAR, ''),
        '.*(^|\\s)#(sponsored|ad|partner)(\\s|$).*',
        'i'
    )                                                              AS is_sponsored,
    REGEXP_LIKE(
        COALESCE(raw_data:video_description::VARCHAR, ''),
        '.*(^|\\s)#(ad|tiktokmademebuyit)(\\s|$).*',
        'i'
    )                                                              AS is_ad,
    FALSE                                                          AS is_pinned
FROM "TIKTOK_DASHBOARD"."PUBLIC"."tiktok_raw"
QUALIFY ROW_NUMBER() OVER (PARTITION BY raw_data:id::VARCHAR ORDER BY loaded_at DESC) = 1;
