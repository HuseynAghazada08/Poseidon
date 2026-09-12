from __future__ import annotations

import pytest

from poseidon.vessel_manager import UnauthorizedVesselError, VesselManager


def test_ingest_valid(tmp_path):
    manager = VesselManager.for_tests(tmp_path)
    reading = manager.ingest("vessel_test_001", {"speed_knots": 10.0, "draft_m": 7.0})
    assert reading.vessel_id == "vessel_test_001"


def test_ingest_unauthorized(tmp_path):
    manager = VesselManager.for_tests(tmp_path)
    with pytest.raises(UnauthorizedVesselError):
        manager.ingest("vessel_unknown_999", {"speed_knots": 5.0})


def test_ingest_updates_state(tmp_path):
    manager = VesselManager.for_tests(tmp_path)
    assert manager.active_vessel_count() == 0
    manager.ingest("vessel_test_001", {"speed_knots": 10.0})
    assert manager.active_vessel_count() == 1
    assert manager.total_reports() == 1


def test_uptime_positive(tmp_path):
    manager = VesselManager.for_tests(tmp_path)
    assert manager.uptime_seconds() >= 0.0


def test_get_vessel_found(tmp_path):
    manager = VesselManager.for_tests(tmp_path)
    v = manager.get_vessel("vessel_test_001")
    assert v is not None
    assert v.id == "vessel_test_001"


def test_get_vessel_not_found(tmp_path):
    manager = VesselManager.for_tests(tmp_path)
    assert manager.get_vessel("nonexistent") is None


def test_last_update_none_initially(tmp_path):
    manager = VesselManager.for_tests(tmp_path)
    assert manager.last_update() is None


def test_last_update_set_after_ingest(tmp_path):
    manager = VesselManager.for_tests(tmp_path)
    manager.ingest("vessel_test_001", {"speed_knots": 5.0})
    assert manager.last_update() is not None
