from __future__ import annotations

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from poseidon.dependencies import get_vessel_manager
from poseidon.main import app
from poseidon.vessel_manager import VesselManager


@pytest.fixture
def client_with_dist_data(tmp_path):
    manager = VesselManager.for_tests(tmp_path)
    timestamps = pd.date_range("2025-03-01", periods=100, freq="h", tz="UTC")
    df = pd.DataFrame(
        {
            "vessel_id": ["vessel_test_001"] * 100,
            "flag_state": ["Netherlands"] * 100,
            "timestamp": timestamps,
            "speed_knots": [5.0, 12.0, 18.0, 25.0] * 25,
            "draft_m": [7.0] * 100,
            "heading_deg": [90.0] * 100,
            "fuel_rate_lph": [150.0] * 100,
        }
    )
    manager._historical_df = df
    app.dependency_overrides[get_vessel_manager] = lambda: manager
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_distribution_returns_html(client_with_dist_data):
    response = client_with_dist_data.get("/distribution/2025/3")
    assert response.status_code == 200
    assert "plotly" in response.text.lower()


def test_distribution_no_data(client_with_dist_data):
    response = client_with_dist_data.get("/distribution/2025/6")
    assert response.status_code == 404


def test_distribution_invalid_month_zero(client_with_dist_data):
    response = client_with_dist_data.get("/distribution/2025/0")
    assert response.status_code == 422


def test_distribution_invalid_month_thirteen(client_with_dist_data):
    response = client_with_dist_data.get("/distribution/2025/13")
    assert response.status_code == 422
