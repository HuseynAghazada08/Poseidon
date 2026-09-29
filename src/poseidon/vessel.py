from __future__ import annotations

from datetime import datetime


class VesselReading:
    """Raw telemetry report. Stored as-is, validated only by pandas later."""

    def __init__(
        self,
        vessel_id: str,
        readings: dict[str, float],
        timestamp: datetime,
    ) -> None:
        self.vessel_id = vessel_id
        self.readings = readings
        self.timestamp = timestamp

    def to_dict(self) -> dict[str, object]:
        return {
            "vessel_id": self.vessel_id,
            "readings": self.readings,
            "timestamp": self.timestamp.isoformat(),
        }


class VesselInfo:
    """Static vessel metadata + last known state."""

    def __init__(
        self,
        id: str,
        location: str,
        longitude: float,
        latitude: float,
        metadata: dict[str, str],
    ) -> None:
        self.id = id
        self.location = location
        self.longitude = longitude
        self.latitude = latitude
        self.metadata = metadata
        self.last_reading: dict[str, float] | None = None
        self.last_update: datetime | None = None
