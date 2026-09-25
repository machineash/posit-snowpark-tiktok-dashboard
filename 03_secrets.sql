-- Phase 3, step 3: credentials as Snowflake Secrets
-- Same idea as .env locally, except these live inside Snowflake instead of
-- a file on disk, and get injected into the container as env vars by the
-- service spec (deploy/service_spec.yaml) rather than being baked into the
-- image. db.py doesn't change at all — it just reads os.environ either way.

CREATE SECRET IF NOT EXISTS "TIKTOK_DASHBOARD"."PUBLIC".tiktok_dashboard_user
    TYPE = GENERIC_STRING
    SECRET_STRING = '<your_snowflake_username>';

CREATE SECRET IF NOT EXISTS "TIKTOK_DASHBOARD"."PUBLIC".tiktok_dashboard_password
    TYPE = GENERIC_STRING
    SECRET_STRING = '<your_snowflake_password>';

SHOW SECRETS IN SCHEMA "TIKTOK_DASHBOARD"."PUBLIC";

-- Note on a more "native" alternative:
-- Snowpark Container Services auto-mounts a short-lived OAuth token at
-- /snowflake/session/token inside every container, which lets a service
-- authenticate back to Snowflake with zero stored password at all
-- (authenticator="oauth" in the connector, reading that file for the
-- token, host=SNOWFLAKE_HOST env var SPCS also injects automatically).
-- That's the more idiomatic pattern for a service that only ever needs to
-- talk to its own account. Kept this project on username/password secrets
-- instead because it's the simpler, more portable path — same code works
-- whether the app runs locally, in plain Docker, or in SPCS — but the
-- OAuth approach is the natural next iteration if this becomes a real
-- internal tool rather than a portfolio piece.
