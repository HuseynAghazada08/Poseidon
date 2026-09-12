from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from poseidon.vessel import VesselInfo

_COLOUR_MAP = {
    "Safe": "green",
    "Moderate": "yellow",
    "Unsafe": "orange",
    "Danger": "red",
    "No data": "black",
}


def _classify_speed(speed: float | None, thresholds: dict[str, float]) -> str:
    if speed is None:
        return "No data"
    if speed <= thresholds["speed_safe"]:
        return "Safe"
    if speed <= thresholds["speed_moderate"]:
        return "Moderate"
    if speed <= thresholds["speed_danger"]:
        return "Unsafe"
    return "Danger"


def create_map(
    vessels: list[VesselInfo],
    thresholds: dict[str, float],
    map_config: dict,  # type: ignore[type-arg]
) -> go.Figure:
    rows = []
    for v in vessels:
        speed = (v.last_reading or {}).get("speed_knots")
        rows.append(
            {
                "vessel_id": v.id,
                "lat": v.latitude,
                "lon": v.longitude,
                "vessel_class": v.metadata.get("vessel_class", ""),
                "home_port": v.metadata.get("home_port", ""),
                "flag_state": v.metadata.get("flag_state", ""),
                "speed_knots": speed if speed is not None else float("nan"),
                "heading_deg": (v.last_reading or {}).get("heading_deg", float("nan")),
                "draft_m": (v.last_reading or {}).get("draft_m", float("nan")),
                "risk_band": _classify_speed(speed, thresholds),
            }
        )
    df = pd.DataFrame(rows)

    fig = px.scatter_map(
        df,
        lat="lat",
        lon="lon",
        color="risk_band",
        color_discrete_map=_COLOUR_MAP,
        hover_name="vessel_id",
        hover_data={
            "vessel_class": True,
            "home_port": True,
            "flag_state": True,
            "speed_knots": ":.1f",
            "heading_deg": ":.0f",
            "draft_m": ":.1f",
            "lat": False,
            "lon": False,
            "risk_band": False,
        },
        zoom=map_config.get("default_zoom", 5),
        center={"lat": map_config["center"]["lat"], "lon": map_config["center"]["lon"]},
        map_style=map_config.get("map_style", "carto-positron"),
        title="Project Poseidon — Real-Time Vessel Traffic",
    )
    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    return fig
