from __future__ import annotations


def test_welcome_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Poseidon" in response.text


def test_status_endpoint(client):
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"healthy", "degraded"}
    assert "uptime_seconds" in data
    assert "active_vessels" in data
    assert "total_reports" in data


def test_status_degraded_when_no_reports(client):
    response = client.get("/status")
    assert response.json()["status"] == "degraded"


def test_status_healthy_after_report(client):
    client.post(
        "/report",
        json={"vessel_id": "vessel_test_001", "readings": {"speed_knots": 5.0}},
    )
    response = client.get("/status")
    assert response.json()["status"] == "healthy"


def test_report_success(client):
    response = client.post(
        "/report",
        json={"vessel_id": "vessel_test_001", "readings": {"speed_knots": 12.0, "draft_m": 8.0}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["vessel_id"] == "vessel_test_001"


def test_unauthorised_vessel_is_rejected(client):
    response = client.post(
        "/report",
        json={"vessel_id": "vessel_not_in_whitelist", "readings": {"speed_knots": 5.0}},
    )
    assert response.status_code == 403


def test_invalid_input_empty_vessel_id(client):
    response = client.post(
        "/report",
        json={"vessel_id": "", "readings": {"speed_knots": 5.0}},
    )
    assert response.status_code == 422


def test_invalid_input_wrong_type(client):
    response = client.post(
        "/report",
        json={"vessel_id": "vessel_test_001", "readings": {"speed_knots": "fast"}},
    )
    assert response.status_code == 422


def test_map_returns_html(client):
    response = client.get("/map")
    assert response.status_code == 200
    assert "plotly" in response.text.lower()


def test_history_not_found(client):
    response = client.get("/history/vessel_unknown_999")
    assert response.status_code == 404


def test_distribution_invalid_month(client):
    response = client.get("/distribution/2025/0")
    assert response.status_code == 422


def test_distribution_invalid_month_high(client):
    response = client.get("/distribution/2025/13")
    assert response.status_code == 422
