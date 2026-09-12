from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from poseidon.vessel import VesselInfo

logger = logging.getLogger(__name__)

WKT_POINT_PATTERN = re.compile(
    r"POINT\s*\(\s*(?P<lon>-?\d+\.?\d*)\s+(?P<lat>-?\d+\.?\d*)\s*\)",
    re.IGNORECASE,
)


def parse_point(wkt: str) -> tuple[float, float]:
    """Parse a single WKT POINT string into (lon, lat) using named capture groups."""
    match = WKT_POINT_PATTERN.fullmatch(wkt.strip())
    if match is None:
        raise ValueError(f"Invalid WKT: {wkt!r}")
    lon = float(match["lon"])
    lat = float(match["lat"])
    if not (-180 <= lon <= 180):
        raise ValueError(f"Longitude {lon} out of range [-180, 180]")
    if not (-90 <= lat <= 90):
        raise ValueError(f"Latitude {lat} out of range [-90, 90]")
    return lon, lat


def load_server_config(config_path: str | Path) -> dict:  # type: ignore[type-arg]
    with open(config_path) as f:
        return json.load(f)  # type: ignore[no-any-return]


def load_vessels(vessels_path: str | Path) -> list[VesselInfo]:
    with open(vessels_path) as f:
        raw: list[dict] = json.load(f)  # type: ignore[type-arg]

    vessels: list[VesselInfo] = []
    for entry in raw:
        vessel_id = entry.get("id", "<unknown>")
        wkt = entry.get("location", "")
        try:
            lon, lat = parse_point(wkt)
        except ValueError as exc:
            logger.warning("Skipping vessel %s: %s", vessel_id, exc)
            continue
        vessels.append(
            VesselInfo(
                id=vessel_id,
                location=wkt,
                longitude=lon,
                latitude=lat,
                metadata=entry.get("metadata", {}),
            )
        )
    logger.info("Loaded %d valid vessels", len(vessels))
    return vessels
