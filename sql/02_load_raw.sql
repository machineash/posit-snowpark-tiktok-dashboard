-- Phase 1: load the scraped TikTok CSV export into tiktok_raw.
--
-- Source: Apify clockworks/tiktok-scraper (profile export, 1,000 most
-- recent videos), exported as CSV.
--
-- Loaded via Snowsight's "Load Data into Table" wizard rather than a
-- manual PUT/COPY, since the wizard handles the file upload + staging
-- in one step. The file format below mirrors what the wizard generates
-- for a standard comma-delimited export with a header row.

CREATE OR REPLACE FILE FORMAT "TIKTOK_DASHBOARD"."PUBLIC".tiktok_csv_format
    TYPE = CSV
    SKIP_HEADER = 1
    FIELD_DELIMITER = ','
    TRIM_SPACE = TRUE
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    REPLACE_INVALID_CHARACTERS = TRUE
    DATE_FORMAT = AUTO
    TIME_FORMAT = AUTO
    TIMESTAMP_FORMAT = AUTO;

-- Load happens via Snowsight's UI wizard (Home > Upload local files),
-- targeting the existing tiktok_raw table so column names/types are
-- already defined and the wizard just matches by name.
--
-- Result: 1,000 rows loaded successfully.
