from __future__ import annotations

from datetime import UTC, datetime

from poseidon.vessel import VesselInfo, VesselReading


def test_vessel_reading_to_dict():
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)
    r = VesselReading(
        vessel_id="vessel_test_001",
        readings={"speed_knots": 10.0},
        timestamp=now,
    )
    d = r.to_dict()
    assert d["vessel_id"] == "vessel_test_001"
    assert d["readings"]["speed_knots"] == 10.0
    assert "2025-01-01" in d["timestamp"]


def test_vessel_info_defaults():
    v = VesselInfo(
        id="vessel_test_001",
        location="POINT(4.0 51.0)",
        longitude=4.0,
        latitude=51.0,
        metadata={"flag_state": "Netherlands"},
    )
    assert v.last_reading is None
    assert v.last_update is None
