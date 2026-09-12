from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from poseidon.dependencies import get_vessel_manager
from poseidon.main import app
from poseidon.vessel_manager import VesselManager


@pytest.fixture
def manager(tmp_path):
    return VesselManager.for_tests(tmp_path)


@pytest.fixture
def client(tmp_path):
    test_manager = VesselManager.for_tests(tmp_path)
    app.dependency_overrides[get_vessel_manager] = lambda: test_manager
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
