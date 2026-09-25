-- Phase 3, step 5: create the service
-- CREATE SERVICE reads the spec from a stage, not straight off your local
-- disk, so it's staged first.

CREATE STAGE IF NOT EXISTS "TIKTOK_DASHBOARD"."PUBLIC".tiktok_dashboard_specs;

-- From a Snowsight worksheet or SnowSQL, upload the file:
--   PUT file://deploy/service_spec.yaml @tiktok_dashboard_specs AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- (SnowSQL runs this from your local machine; Snowsight worksheets can't
-- PUT local files directly — use SnowSQL or the Snowflake CLI for this one
-- step, everything else here can run in Snowsight.)

CREATE SERVICE IF NOT EXISTS "TIKTOK_DASHBOARD"."PUBLIC".tiktok_dashboard_service
    IN COMPUTE POOL tiktok_dashboard_pool
    FROM @tiktok_dashboard_specs
    SPECIFICATION_FILE = 'service_spec.yaml'
    MIN_INSTANCES = 1
    MAX_INSTANCES = 1;

-- Watch it come up
SELECT SYSTEM$GET_SERVICE_STATUS('tiktok_dashboard_service');
CALL SYSTEM$GET_SERVICE_LOGS('tiktok_dashboard_service', '0', 'tiktok-dashboard', 100);

-- Once RUNNING, get the public URL
SHOW ENDPOINTS IN SERVICE tiktok_dashboard_service;
