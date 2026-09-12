from __future__ import annotations

import json

import pytest

from poseidon.config_loader import load_vessels, parse_point


def test_parse_point_basic():
    lon, lat = parse_point("POINT(4.4792 51.9225)")
    assert abs(lon - 4.4792) < 1e-4
    assert abs(lat - 51.9225) < 1e-4


def test_parse_point_with_spaces():
    lon, lat = parse_point("POINT( 9.9937   53.5507 )")
    assert abs(lon - 9.9937) < 1e-4
    assert abs(lat - 53.5507) < 1e-4


def test_parse_point_case_insensitive():
    lon, lat = parse_point("point(4.4792 51.9225)")
    assert abs(lon - 4.4792) < 1e-4


def test_parse_point_negative_lon():
    lon, lat = parse_point("POINT(-5.0 51.0)")
    assert lon == -5.0


def test_parse_point_invalid_raises():
    with pytest.raises(ValueError):
        parse_point("NOT_A_POINT(1 2)")


def test_parse_point_split_not_allowed():
    # confirm no split/replace used: regex parse on unusual whitespace
    lon, lat = parse_point("POINT(  10.2039  56.1629  )")
    assert abs(lon - 10.2039) < 1e-4


def test_parse_point_out_of_range_lon():
    with pytest.raises(ValueError, match="Longitude"):
        parse_point("POINT(200.0 51.0)")


def test_parse_point_out_of_range_lat():
    with pytest.raises(ValueError, match="Latitude"):
        parse_point("POINT(4.0 95.0)")


def test_load_vessels_valid(tmp_path):
    data = [
        {
            "id": "vessel_test_001",
            "location": "POINT(4.4792 51.9225)",
            "metadata": {
                "flag_state": "Netherlands",
                "home_port": "Rotterdam",
                "vessel_class": "container",
                "commissioned_date": "2021-01-01",
            },
        }
    ]
    p = tmp_path / "vessels.json"
    p.write_text(json.dumps(data))
    vessels = load_vessels(p)
    assert len(vessels) == 1
    assert vessels[0].id == "vessel_test_001"
    assert abs(vessels[0].longitude - 4.4792) < 1e-4


def test_load_vessels_skips_invalid_wkt(tmp_path):
    data = [
        {"id": "bad", "location": "NOT_WKT", "metadata": {}},
        {
            "id": "vessel_test_002",
            "location": "POINT(9.9937 53.5507)",
            "metadata": {
                "flag_state": "Germany",
                "home_port": "Hamburg",
                "vessel_class": "container",
                "commissioned_date": "2018-01-01",
            },
        },
    ]
    p = tmp_path / "vessels.json"
    p.write_text(json.dumps(data))
    vessels = load_vessels(p)
    assert len(vessels) == 1
    assert vessels[0].id == "vessel_test_002"
