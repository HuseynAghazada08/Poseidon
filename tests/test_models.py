from __future__ import annotations

import pytest
from pydantic import ValidationError

from poseidon.models import IngestRequest, StatusResponse


def test_ingest_request_valid():
    req = IngestRequest(
        vessel_id="vessel_rotterdam_001",
        readings={"speed_knots": 12.5, "draft_m": 8.0},
    )
    assert req.vessel_id == "vessel_rotterdam_001"


def test_ingest_request_empty_vessel_id():
    with pytest.raises(ValidationError):
        IngestRequest(vessel_id="", readings={})


def test_ingest_request_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        IngestRequest(vessel_id="v1", readings={}, extra_field="bad")  # type: ignore[call-arg]


def test_ingest_request_wrong_type_strict():
    with pytest.raises(ValidationError):
        IngestRequest(vessel_id=123, readings={})  # type: ignore[arg-type]


def test_status_response_degraded():
    r = StatusResponse(
        status="degraded",
        uptime_seconds=10.0,
        active_vessels=0,
        total_reports=0,
        last_update=None,
    )
    assert r.status == "degraded"
