from __future__ import annotations

from datetime import UTC, datetime

from poseidon.persistence import append_reading_json, load_readings_json
from poseidon.vessel import VesselReading


def test_roundtrip_json(tmp_path):
    f = tmp_path / "readings.json"
    r = VesselReading(
        vessel_id="vessel_test_001",
        readings={"speed_knots": 10.0},
        timestamp=datetime(2025, 1, 1, tzinfo=UTC),
    )
    append_reading_json(f, r)
    loaded = load_readings_json(f)
    assert len(loaded) == 1
    assert loaded[0]["vessel_id"] == "vessel_test_001"


def test_load_missing_file_returns_empty(tmp_path):
    result = load_readings_json(tmp_path / "nonexistent.json")
    assert result == []


def test_load_corrupt_file_returns_empty(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text("not json {{{{")
    result = load_readings_json(f)
    assert result == []


def test_multiple_appends(tmp_path):
    f = tmp_path / "readings.json"
    for i in range(3):
        r = VesselReading(
            vessel_id="vessel_test_001",
            readings={"speed_knots": float(i)},
            timestamp=datetime(2025, 1, 1, i, tzinfo=UTC),
        )
        append_reading_json(f, r)
    loaded = load_readings_json(f)
    assert len(loaded) == 3
