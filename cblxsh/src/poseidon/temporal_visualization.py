from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from poseidon.data_cleaning import DataCleaner

_TRACE_COLOURS = {
    "speed_knots": "#1f77b4",
    "draft_m": "#ff7f0e",
    "heading_deg": "#2ca02c",
    "fuel_rate_lph": "#d62728",
}

_BAND_COLOURS = {
    "Safe": "green",
    "Moderate": "yellow",
    "Unsafe": "orange",
    "Danger": "red",
}


def create_time_series(df: pd.DataFrame, vessel_id: str) -> go.Figure:
    vessel_df = df[df["vessel_id"] == vessel_id].sort_values("timestamp")

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        subplot_titles=("Speed (knots)", "Draft (m)", "Heading (deg)", "Fuel Rate (l/h)"),
        vertical_spacing=0.05,
    )

    traces = [
        ("speed_knots", 1),
        ("draft_m", 2),
        ("heading_deg", 3),
        ("fuel_rate_lph", 4),
    ]
    for col, row in traces:
        fig.add_trace(
            go.Scatter(
                x=vessel_df["timestamp"],
                y=vessel_df[col],
                mode="lines",
                name=col,
                line={"color": _TRACE_COLOURS[col]},
            ),
            row=row,
            col=1,
        )

    fig.update_xaxes(rangeslider_visible=True, row=4, col=1)
    fig.update_layout(
        hovermode="x unified",
        title=f"Time Series — {vessel_id}",
        height=900,
        showlegend=True,
    )
    return fig


def create_distribution_chart(
    df: pd.DataFrame,
    thresholds: dict[str, float],
    year: int,
    month: int,
) -> go.Figure:
    counts = DataCleaner.distribution_by_flag(df, thresholds, year, month)

    fig = go.Figure()
    for band in ["Safe", "Moderate", "Unsafe", "Danger"]:
        band_data = counts[counts["risk_band"] == band]
        fig.add_trace(
            go.Bar(
                name=band,
                x=band_data["flag_state"],
                y=band_data["percentage"],
                marker_color=_BAND_COLOURS[band],
                text=band_data["percentage"].round(1),
                texttemplate="%{text:.1f}%",
                textposition="inside",
                insidetextanchor="middle",
            )
        )

    fig.update_layout(
        barmode="stack",
        title=f"Speed Distribution by Flag State — {year}/{month:02d}",
        yaxis={"range": [0, 100], "title": "Percentage (%)"},
        xaxis_title="Flag State",
        legend_title="Risk Band",
        uniformtext_minsize=8,
        uniformtext_mode="hide",
    )
    return fig
