from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from poseidon.vessel_manager import VesselManager

_vessel_manager: VesselManager | None = None


def get_vessel_manager() -> VesselManager:
    if _vessel_manager is None:
        msg = "VesselManager not initialised"
        raise RuntimeError(msg)
    return _vessel_manager


def set_vessel_manager(manager: VesselManager) -> None:
    global _vessel_manager
    _vessel_manager = manager


def reset_vessel_manager() -> None:
    global _vessel_manager
    _vessel_manager = None


VesselManagerDep = Annotated[VesselManager, Depends(get_vessel_manager)]
