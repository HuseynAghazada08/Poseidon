from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd

from poseidon.vessel import VesselReading

logger = logging.getLogger(__name__)


def load_readings_json(storage_file: str | Path) -> list[dict]:  # type: ignore[type-arg]
    path = Path(storage_file)
    if not path.exists():
        return []
    try:
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, list):
            return data  # type: ignore[return-value]
        logger.warning("readings.json has unexpected shape; starting fresh")
        return []
    except Exception as exc:
        logger.warning("Could not read %s: %s; starting fresh", path, exc)
        return []


def append_reading_json(storage_file: str | Path, reading: VesselReading) -> None:
    path = Path(storage_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_readings_json(path)
    existing.append(reading.to_dict())
    try:
        with open(path, "w") as f:
            json.dump(existing, f, indent=2, default=str)
    except Exception as exc:
        logger.error("Failed to persist reading: %s", exc)


def load_historical_csv(csv_file: str | Path) -> pd.DataFrame:
    path = Path(csv_file)
    if not path.exists():
        logger.warning("Historical CSV not found at %s", path)
        return pd.DataFrame()
    try:
        df = pd.read_csv(str(path), dtype_backend="pyarrow")
        return df
    except Exception as exc:
        logger.error("Failed to load historical CSV %s: %s", path, exc)
        return pd.DataFrame()
