"""
Phase 2: Shiny for Python dashboard over tiktok_videos (Snowflake).

Sections:
  - engagement over time (views/likes trend by post_date)
  - top posts table (video_id, post_date, metrics only — no caption/cover_url)
  - organic vs. sponsored comparison
  - duration vs. performance (binned)

Sidebar filters: date range, sponsored/organic toggle.
"""

from datetime import date

import pandas as pd
import plotly.express as px
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_widget

from db import fetch_videos

# ---- one-time bounds for the date range picker --------------------------
# Falls back to sane defaults if Snowflake isn't reachable yet (e.g. .env
# not filled in), so the app still loads and shows a clear error later
# when a filter actually tries to query.
try:
    _bounds_df = fetch_videos()
    MIN_DATE = _bounds_df["post_date"].min().date() if not _bounds_df.empty else date(2020, 1, 1)
    MAX_DATE = _bounds_df["post_date"].max().date() if not _bounds_df.empty else date.today()
except Exception:
    MIN_DATE = date(2020, 1, 1)
    MAX_DATE = date.today()

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h4("Filters"),
        ui.input_date_range(
            "date_range", "Date range", start=MIN_DATE, end=MAX_DATE,
            min=MIN_DATE, max=MAX_DATE,
        ),
        ui.input_radio_buttons(
            "sponsor_filter", "Post type",
            choices={"all": "All", "organic": "Organic only", "sponsored": "Sponsored/ad only"},
            selected="all",
        ),
        ui.hr(),
        ui.p(
            "Top posts show video ID, date, and metrics only — "
            "no captions or cover images.",
            class_="text-muted small",
        ),
        width=280,
    ),
    ui.h2("TikTok Engagement Dashboard"),
    ui.layout_columns(
        ui.value_box("Total videos", ui.output_text("kpi_count")),
        ui.value_box("Total views", ui.output_text("kpi_views")),
        ui.value_box("Avg. engagement rate", ui.output_text("kpi_engagement")),
        fill=False,
    ),
    ui.card(
        ui.card_header("Engagement over time"),
        output_widget("engagement_over_time", height="380px"),
        height="520px",
    ),
    ui.layout_columns(
        ui.card(
            ui.card_header("Organic vs. sponsored"),
            output_widget("organic_vs_sponsored", height="380px"),
            height="520px",
        ),
        ui.card(
            ui.card_header("Duration vs. performance"),
            output_widget("duration_vs_performance", height="380px"),
            height="520px",
        ),
    ),
    ui.card(
        ui.card_header("Top posts"),
        ui.output_data_frame("top_posts"),
        height="560px",
    ),
    title="TikTok Dashboard",
    fillable=True,
)


def server(input, output, session):

    @reactive.calc
    def filtered_df() -> pd.DataFrame:
        start, end = input.date_range()
        sponsored_only = {"all": None, "organic": False, "sponsored": True}[input.sponsor_filter()]
        df = fetch_videos(start_date=start, end_date=end, sponsored_only=sponsored_only)
        if not df.empty:
            df["engagement_rate"] = (
                (df["likes"] + df["comments"] + df["shares"] + df["saves"]) / df["views"].replace(0, pd.NA)
            )
        return df

    # ---- KPIs -------------------------------------------------------
    @render.text
    def kpi_count():
        return f"{len(filtered_df()):,}"

    @render.text
    def kpi_views():
        df = filtered_df()
        return f"{int(df['views'].sum()):,}" if not df.empty else "0"

    @render.text
    def kpi_engagement():
        df = filtered_df()
        if df.empty or df["engagement_rate"].dropna().empty:
            return "—"
        return f"{df['engagement_rate'].mean() * 100:.1f}%"

    # ---- engagement over time ----------------------------------------
    @render_widget
    def engagement_over_time():
        df = filtered_df()
        if df.empty:
            return px.line(title="No data for this filter")
        daily = (
            df.set_index("post_date")
            .sort_index()[["views", "likes", "comments", "shares", "saves"]]
            .resample("W")
            .sum()
            .reset_index()
        )
        # Convert to plain ISO date strings before handing off to plotly —
        # the shinywidgets/FigureWidget bridge otherwise sometimes
        # serializes pandas Timestamps as raw int64 nanoseconds, showing up
        # as huge numbers on the x-axis instead of dates. Explicitly typing
        # the axis as "date" (rather than "category") lets plotly parse
        # those ISO strings back into real dates and auto-space/format the
        # ticks (by month, etc.) instead of drawing one label per week.
        daily["post_date"] = daily["post_date"].dt.strftime("%Y-%m-%d")
        long = daily.melt(id_vars="post_date", var_name="metric", value_name="value")
        fig = px.line(
            long, x="post_date", y="value", color="metric",
            labels={"post_date": "Week", "value": "Count", "metric": "Metric"},
        )
        fig.update_xaxes(type="date", tickformat="%b %Y", nticks=8)
        fig.update_layout(legend_title_text="", height=380, margin=dict(l=60, r=20, t=20, b=40))
        return fig

    # ---- organic vs. sponsored -----------------------------------------
    @render_widget
    def organic_vs_sponsored():
        df = filtered_df()
        if df.empty:
            return px.bar(title="No data for this filter")
        d = df.copy()
        d["post_type"] = d.apply(
            lambda r: "Sponsored/Ad" if (r["is_sponsored"] or r["is_ad"]) else "Organic", axis=1
        )
        summary = (
            d.groupby("post_type")[["views", "likes", "comments", "shares", "saves"]]
            .mean()
            .reset_index()
            .melt(id_vars="post_type", var_name="metric", value_name="avg_value")
        )
        fig = px.bar(
            summary, x="metric", y="avg_value", color="post_type", barmode="group",
            labels={"metric": "Metric", "avg_value": "Average per post", "post_type": ""},
        )
        fig.update_yaxes(tickformat="~s")
        fig.update_layout(height=380, margin=dict(l=60, r=20, t=20, b=40))
        return fig

    # ---- duration vs. performance ---------------------------------------
    @render_widget
    def duration_vs_performance():
        df = filtered_df()
        if df.empty:
            return px.bar(title="No data for this filter")
        d = df.copy()
        bins = [0, 15, 30, 60, 120, 300, float("inf")]
        labels = ["0-15s", "15-30s", "30-60s", "1-2m", "2-5m", "5m+"]
        d["duration_bucket"] = pd.cut(d["duration_secs"], bins=bins, labels=labels, right=False)
        summary = (
            d.groupby("duration_bucket", observed=True)[["views", "likes"]]
            .mean()
            .reset_index()
        )
        fig = px.bar(
            summary, x="duration_bucket", y="views",
            labels={"duration_bucket": "Video length", "views": "Avg. views"},
        )
        fig.update_yaxes(tickformat="~s")
        fig.update_layout(height=380, margin=dict(l=60, r=20, t=20, b=40))
        return fig

    # ---- top posts table --------------------------------------------
    @render.data_frame
    def top_posts():
        df = filtered_df()
        if df.empty:
            return render.DataGrid(
                pd.DataFrame(columns=["video_id", "post_date", "views", "likes", "comments", "shares", "saves"]),
                height="450px",
            )
        cols = ["video_id", "post_date", "views", "likes", "comments", "shares", "saves", "is_sponsored", "is_ad"]
        out = df[cols].sort_values("views", ascending=False).head(25).copy()
        out["post_date"] = out["post_date"].dt.strftime("%Y-%m-%d")
        return render.DataGrid(out, filters=True, height="450px")


app = App(app_ui, server)