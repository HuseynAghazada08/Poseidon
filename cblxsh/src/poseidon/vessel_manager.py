from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from poseidon.data_cleaning import DataCleaner
from poseidon.persistence import (
    append_reading_json,
    load_historical_csv,
    load_readings_json,
)
from poseidon.vessel import VesselInfo, VesselReading

logger = logging.getLogger(__name__)


class UnauthorizedVesselError(Exception):
    pass


class InvalidReportError(Exception):
    pass


class VesselManager:
    def __init__(
        self,
        vessels: list[VesselInfo],
        storage_file: str | Path,
        thresholds: dict[str, float],
        historical_df: pd.DataFrame | None = None,
    ) -> None:
        self._vessels: dict[str, VesselInfo] = {v.id: v for v in vessels}
        self._storage_file = Path(storage_file)
        self._thresholds = thresholds
        self._historical_df = historical_df if historical_df is not None else pd.DataFrame()
        self._total_reports = 0
        self._last_update: datetime | None = None
        self._start_time = datetime.now(tz=UTC)

    @classmethod
    def for_tests(cls, tmp_path: Path) -> VesselManager:
        from poseidon.vessel import VesselInfo

        vessels = [
            VesselInfo(
                id="vessel_test_001",
                location="POINT(4.4792 51.9225)",
                longitude=4.4792,
                latitude=51.9225,
                metadata={
                    "flag_state": "Netherlands",
                    "home_port": "Rotterdam",
                    "vessel_class": "container",
                    "commissioned_date": "2021-04-12",
                },
            )
        ]
        storage = tmp_path / "readings.json"
        thresholds = {
            "speed_safe": 10.0,
            "speed_moderate": 15.0,
            "speed_danger": 22.0,
            "draft_safe": 6.0,
            "draft_moderate": 9.0,
            "draft_danger": 12.0,
        }
        return cls(vessels=vessels, storage_file=storage, thresholds=thresholds)

    def hydrate_from_storage(self) -> None:
        records = load_readings_json(self._storage_file)
        for rec in records:
            vid = rec.get("vessel_id", "")
            if vid in self._vessels:
                self._vessels[vid].last_reading = rec.get("readings")
                ts_raw = rec.get("timestamp")
                if ts_raw:
                    try:
                        self._vessels[vid].last_update = datetime.fromisoformat(ts_raw)
                    except ValueError:
                        pass
                self._total_reports += 1
        if records:
            self._last_update = datetime.now(tz=UTC)
        logger.info("Hydrated %d reports from storage", len(records))

    def ingest(self, vessel_id: str, readings: dict[str, float]) -> VesselReading:
        if vessel_id not in self._vessels:
            raise UnauthorizedVesselError(f"Vessel {vessel_id!r} is not authorised")

        valid, errors = DataCleaner.validate_report(readings)
        if not valid:
            raise InvalidReportError("; ".join(errors))

        now = datetime.now(tz=UTC)
        reading = VesselReading(vessel_id=vessel_id, readings=readings, timestamp=now)

        self._vessels[vessel_id].last_reading = readings
        self._vessels[vessel_id].last_update = now
        self._total_reports += 1
        self._last_update = now

        append_reading_json(self._storage_file, reading)
        return reading

    def get_vessel(self, vessel_id: str) -> VesselInfo | None:
        return self._vessels.get(vessel_id)

    def get_all_vessels(self) -> list[VesselInfo]:
        return list(self._vessels.values())

    def get_historical_df(self) -> pd.DataFrame:
        return self._historical_df

    def get_thresholds(self) -> dict[str, float]:
        return self._thresholds

    def active_vessel_count(self) -> int:
        return sum(1 for v in self._vessels.values() if v.last_reading is not None)

    def total_reports(self) -> int:
        return self._total_reports

    def last_update(self) -> datetime | None:
        return self._last_update

    def uptime_seconds(self) -> float:
        delta = datetime.now(tz=UTC) - self._start_time
        return delta.total_seconds()

    def load_historical(self, csv_file: str | Path) -> None:
        raw = load_historical_csv(csv_file)
        if raw.empty:
            return
        cleaned = DataCleaner.clean_historical_batch(raw)
        self._historical_df = cleaned
