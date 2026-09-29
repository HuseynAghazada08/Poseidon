from __future__ import annotations

import pandas as pd

from poseidon.data_cleaning import DataCleaner

THRESHOLDS = {
    "speed_safe": 10.0,
    "speed_moderate": 15.0,
    "speed_danger": 22.0,
}


def _make_df(rows: list[dict]) -> pd.DataFrame:  # type: ignore[type-arg]
    return pd.DataFrame(rows)


def test_validate_report_valid():
    ok, errors = DataCleaner.validate_report({"speed_knots": 12.0, "draft_m": 8.0})
    assert ok
    assert errors == []


def test_validate_report_negative_speed():
    ok, errors = DataCleaner.validate_report({"speed_knots": -1.0})
    assert not ok
    assert any("speed_knots" in e for e in errors)


def test_validate_report_bad_heading():
    ok, errors = DataCleaner.validate_report({"heading_deg": 400.0})
    assert not ok


def test_clean_historical_drops_negatives():
    df = _make_df(
        [
            {
                "vessel_id": "v1",
                "timestamp": "2025-01-01T00:00:00Z",
                "speed_knots": -1.0,
                "draft_m": 5.0,
                "fuel_rate_lph": 100.0,
                "heading_deg": 90.0,
            },
            {
                "vessel_id": "v1",
                "timestamp": "2025-01-01T01:00:00Z",
                "speed_knots": 10.0,
                "draft_m": 5.0,
                "fuel_rate_lph": 100.0,
                "heading_deg": 90.0,
            },
        ]
    )
    cleaned = DataCleaner.clean_historical_batch(df)
    assert len(cleaned) == 1


def test_clean_historical_drops_speed_over_50():
    df = _make_df(
        [
            {
                "vessel_id": "v1",
                "timestamp": "2025-01-01T00:00:00Z",
                "speed_knots": 55.0,
                "draft_m": 5.0,
                "fuel_rate_lph": 100.0,
                "heading_deg": 90.0,
            },
            {
                "vessel_id": "v1",
                "timestamp": "2025-01-01T01:00:00Z",
                "speed_knots": 10.0,
                "draft_m": 5.0,
                "fuel_rate_lph": 100.0,
                "heading_deg": 90.0,
            },
        ]
    )
    cleaned = DataCleaner.clean_historical_batch(df)
    assert len(cleaned) == 1


def test_clean_historical_drops_missing_vessel_id():
    df = _make_df(
        [
            {
                "vessel_id": None,
                "timestamp": "2025-01-01T00:00:00Z",
                "speed_knots": 10.0,
                "draft_m": 5.0,
                "fuel_rate_lph": 100.0,
                "heading_deg": 90.0,
            },
            {
                "vessel_id": "v1",
                "timestamp": "2025-01-01T01:00:00Z",
                "speed_knots": 10.0,
                "draft_m": 5.0,
                "fuel_rate_lph": 100.0,
                "heading_deg": 90.0,
            },
        ]
    )
    cleaned = DataCleaner.clean_historical_batch(df)
    assert len(cleaned) == 1


def test_parse_wkt_column():
    s = pd.Series(["POINT(4.4792 51.9225)", "POINT(9.9937 53.5507)"])
    coords = DataCleaner.parse_wkt_column(s)
    assert "lon" in coords.columns
    assert "lat" in coords.columns
    assert abs(coords["lon"].iloc[0] - 4.4792) < 1e-3


def test_categorise_by_speed():
    df = _make_df(
        [
            {"vessel_id": "v1", "speed_knots": 5.0},
            {"vessel_id": "v1", "speed_knots": 12.0},
            {"vessel_id": "v1", "speed_knots": 18.0},
            {"vessel_id": "v1", "speed_knots": 25.0},
        ]
    )
    result = DataCleaner.categorise_by_speed(df, THRESHOLDS)
    bands = result["risk_band"].astype(str).tolist()
    assert bands[0] == "Safe"
    assert bands[1] == "Moderate"
    assert bands[2] == "Unsafe"
    assert bands[3] == "Danger"


def test_distribution_by_flag_returns_empty_for_missing_period():
    df = _make_df(
        [
            {
                "vessel_id": "v1",
                "flag_state": "Netherlands",
                "timestamp": pd.Timestamp("2025-01-01T00:00:00Z"),
                "speed_knots": 10.0,
            },
        ]
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    result = DataCleaner.distribution_by_flag(df, THRESHOLDS, 2025, 6)
    assert result.empty
