from __future__ import annotations

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from poseidon.dependencies import get_vessel_manager
from poseidon.main import app
from poseidon.vessel_manager import VesselManager


@pytest.fixture
def client_with_history(tmp_path):
    manager = VesselManager.for_tests(tmp_path)
    # build minimal historical df
    timestamps = pd.date_range("2025-01-01", periods=24, freq="h", tz="UTC")
    df = pd.DataFrame(
        {
            "vessel_id": ["vessel_test_001"] * 24,
            "flag_state": ["Netherlands"] * 24,
            "timestamp": timestamps,
            "speed_knots": [10.0] * 24,
            "draft_m": [7.0] * 24,
            "heading_deg": [90.0] * 24,
            "fuel_rate_lph": [150.0] * 24,
        }
    )
    manager._historical_df = df
    app.dependency_overrides[get_vessel_manager] = lambda: manager
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_history_returns_html(client_with_history):
    response = client_with_history.get("/history/vessel_test_001")
    assert response.status_code == 200
    assert "plotly" in response.text.lower()


def test_history_unknown_vessel(client_with_history):
    response = client_with_history.get("/history/vessel_unknown_999")
    assert response.status_code == 404
