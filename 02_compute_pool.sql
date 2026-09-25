-- Phase 3, step 2: compute pool
-- This is the actual compute the dashboard container runs on. A dashboard
-- over 1,000 rows needs essentially nothing, so smallest instance family,
-- single node, and auto-suspend so it's not burning credits while idle.

CREATE COMPUTE POOL IF NOT EXISTS tiktok_dashboard_pool
    MIN_NODES = 1
    MAX_NODES = 1
    INSTANCE_FAMILY = CPU_X64_XS
    AUTO_SUSPEND_SECS = 300
    AUTO_RESUME = TRUE;

SHOW COMPUTE POOLS LIKE 'tiktok_dashboard_pool';

-- Needs ACCOUNTADMIN or a role granted CREATE COMPUTE POOL on the account.
-- If this errors with an insufficient-privileges message, that's the role
-- to check first.
