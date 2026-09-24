"""
Snowflake connection + query helpers for the TikTok dashboard.

Credentials come from environment variables (loaded from a local .env
file via python-dotenv in dev; in Phase 3 these get set as container
env vars / secrets instead — same code, no changes needed).

Every query here is written to pull only the columns the dashboard
needs. `caption` and `cover_url` are never selected, even though they
exist in tiktok_videos — keeping that content-identifying data out of
the app entirely rather than fetching and hiding it.
"""

import os

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

TABLE = "tiktok_videos"

# Columns the dashboard is allowed to touch. caption/cover_url excluded
# on purpose — see module docstring.
SAFE_COLUMNS = [
    "video_id",
    "video_url",
    "post_date",
    "views",
    "likes",
    "comments",
    "shares",
    "saves",
    "duration_secs",
    "is_sponsored",
    "is_ad",
    "is_pinned",
]


def get_connection():
    required = ["SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD"]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        raise RuntimeError(
            f"Missing Snowflake env vars: {', '.join(missing)}. "
            "Copy .env.example to .env and fill in your credentials."
        )

    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ.get("SNOWFLAKE_WAREHOUSE"),
        database=os.environ.get("SNOWFLAKE_DATABASE", "TIKTOK_DASHBOARD"),
        schema=os.environ.get("SNOWFLAKE_SCHEMA", "PUBLIC"),
        role=os.environ.get("SNOWFLAKE_ROLE"),
    )


def fetch_videos(start_date=None, end_date=None, sponsored_only=None) -> pd.DataFrame:
    """
    Pull rows from tiktok_videos, filtered at the SQL level.

    sponsored_only: None (all), True (is_sponsored or is_ad), or
    False (organic only).
    """
    cols = ", ".join(SAFE_COLUMNS)
    where = ["1=1"]
    params = []

    if start_date is not None:
        where.append("post_date >= %s")
        params.append(start_date)
    if end_date is not None:
        where.append("post_date <= %s")
        params.append(end_date)
    if sponsored_only is True:
        where.append("(is_sponsored = TRUE OR is_ad = TRUE)")
    elif sponsored_only is False:
        where.append("(is_sponsored = FALSE AND is_ad = FALSE)")

    query = f"""
        SELECT {cols}
        FROM {TABLE}
        WHERE {" AND ".join(where)}
        ORDER BY post_date DESC
    """

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        df = cur.fetch_pandas_all()
    finally:
        conn.close()

    df.columns = [c.lower() for c in df.columns]
    if not df.empty:
        df["post_date"] = pd.to_datetime(df["post_date"])
    return df
