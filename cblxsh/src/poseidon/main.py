from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException
from fastapi import Path as FPath
from fastapi.responses import HTMLResponse

from poseidon.config_loader import load_server_config, load_vessels
from poseidon.data_cleaning import DataCleaner
from poseidon.dependencies import (
    VesselManagerDep,
    reset_vessel_manager,
    set_vessel_manager,
)
from poseidon.models import IngestRequest, IngestResponse, StatusResponse, VesselInfoRead
from poseidon.temporal_visualization import create_distribution_chart, create_time_series
from poseidon.vessel_manager import InvalidReportError, UnauthorizedVesselError, VesselManager
from poseidon.visualization import create_map

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(os.getenv("CONFIG_PATH", "config/server_config.json"))
_VESSELS_PATH = Path(os.getenv("VESSELS_PATH", "config/vessels.json"))

_NAV = (
    "<div style='font-family:sans-serif;padding:6px 10px;background:#333'>"
    "<a href='/' style='color:#fff;text-decoration:none;font-weight:bold'>&#8592; Main Page</a>"
    "</div>"
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:  # type: ignore[type-arg]
    config = load_server_config(_CONFIG_PATH)
    vessels = load_vessels(_VESSELS_PATH)
    manager = VesselManager(
        vessels=vessels,
        storage_file=config["storage_file"],
        thresholds=config["thresholds"],
    )
    manager.load_historical(config["historical_data_file"])
    manager.hydrate_from_storage()
    set_vessel_manager(manager)
    app.state.config = config
    logger.info("Project Poseidon started")
    yield
    reset_vessel_manager()
    logger.info("Project Poseidon stopped")


app = FastAPI(title="Project Poseidon", version="1.0.0", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
def welcome() -> str:
    return """
    <html><head><title>Project Poseidon</title></head><body>
    <h1>Project Poseidon — Maritime Vessel Traffic Monitor</h1>
    <ul>
      <li><a href="/map">Real-Time Map</a></li>
      <li><a href="/status">System Status (JSON)</a></li>
      <li><a href="/vessels">Vessel List (JSON)</a></li>
      <li><a href="/history/vessel_rotterdam_001">History (example vessel)</a></li>
      <li><a href="/distribution/2025/1">Distribution (example: 2025/01)</a></li>
      <li><a href="/docs">API Documentation</a></li>
    </ul>
    </body></html>
    """


@app.get("/vessels", response_model=list[VesselInfoRead])
def vessels(manager: VesselManagerDep) -> list[VesselInfoRead]:
    return [VesselInfoRead.model_validate(v) for v in manager.get_all_vessels()]


@app.post("/report", response_model=IngestResponse)
def report(request: IngestRequest, manager: VesselManagerDep) -> IngestResponse:
    try:
        reading = manager.ingest(request.vessel_id, request.readings)
    except UnauthorizedVesselError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except InvalidReportError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return IngestResponse(
        status="ok",
        message="Reading ingested",
        vessel_id=reading.vessel_id,
        timestamp=reading.timestamp,
    )


@app.get("/map", response_class=HTMLResponse)
def map_view(manager: VesselManagerDep) -> str:
    config = app.state.config
    fig = create_map(
        vessels=manager.get_all_vessels(),
        thresholds=manager.get_thresholds(),
        map_config=config["map_config"],
    )
    return fig.to_html(include_plotlyjs="cdn", full_html=True)


@app.get("/status", response_model=StatusResponse)
def status(manager: VesselManagerDep) -> StatusResponse:
    last = manager.last_update()
    health = "healthy" if manager.active_vessel_count() > 0 else "degraded"
    return StatusResponse(
        status=health,
        uptime_seconds=manager.uptime_seconds(),
        active_vessels=manager.active_vessel_count(),
        total_reports=manager.total_reports(),
        last_update=last,
    )


@app.get("/history/{vessel_id}", response_class=HTMLResponse)
def history(
    vessel_id: Annotated[str, FPath(min_length=1)],
    manager: VesselManagerDep,
) -> str:
    vessel = manager.get_vessel(vessel_id)
    if vessel is None:
        raise HTTPException(status_code=404, detail=f"Vessel {vessel_id!r} not found")

    df = manager.get_historical_df()
    if df.empty or vessel_id not in df["vessel_id"].values:
        raise HTTPException(status_code=404, detail=f"No historical data for {vessel_id!r}")

    all_ids = sorted(v.id for v in manager.get_all_vessels())
    options = "\n".join(
        f'<option value="{vid}" {"selected" if vid == vessel_id else ""}>{vid}</option>'
        for vid in all_ids
    )
    selector = (
        "<div style='font-family:sans-serif;padding:10px;background:#f5f5f5'>"
        "<label><b>Vessel: </b></label>"
        f"<select onchange=\"location='/history/'+this.value\">{options}</select>"
        "</div>"
    )

    fig = create_time_series(df, vessel_id)
    chart_body = fig.to_html(include_plotlyjs="cdn", full_html=False)
    return f"<html><body>{_NAV}{selector}{chart_body}</body></html>"


@app.get("/distribution/{year}/{month}", response_class=HTMLResponse)
def distribution(
    year: Annotated[int, FPath(ge=2020, le=2100)],
    month: Annotated[int, FPath(ge=1, le=12)],
    manager: VesselManagerDep,
) -> str:
    df = manager.get_historical_df()
    if df.empty:
        raise HTTPException(status_code=404, detail="No historical data available")

    counts = DataCleaner.distribution_by_flag(df, manager.get_thresholds(), year, month)
    if counts.empty:
        raise HTTPException(status_code=404, detail=f"No data for {year}/{month:02d}")

    available_years = sorted(df["timestamp"].dt.year.unique().tolist())
    year_options = "\n".join(
        f'<option value="{y}" {"selected" if y == year else ""}>{y}</option>'
        for y in available_years
    )
    _month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    month_options = "\n".join(
        f'<option value="{m}" {"selected" if m == month else ""}>'
        f"{m:02d} — {_month_names[m - 1]}</option>"
        for m in range(1, 13)
    )
    selector = (
        "<div style='font-family:sans-serif;padding:10px;background:#f5f5f5'>"
        f"<label><b>Year: </b></label><select id='yr'>{year_options}</select>"
        "&nbsp;&nbsp;"
        f"<label><b>Month: </b></label><select id='mo'>{month_options}</select>"
        "&nbsp;&nbsp;"
        "<button onclick=\"location='/distribution/'+document.getElementById('yr').value"
        "+'/'+document.getElementById('mo').value\">Go</button>"
        "</div>"
    )

    fig = create_distribution_chart(df, manager.get_thresholds(), year, month)
    chart_body = fig.to_html(include_plotlyjs="cdn", full_html=False)
    return f"<html><body>{_NAV}{selector}{chart_body}</body></html>"
