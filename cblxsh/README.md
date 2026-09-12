# Project Poseidon - Maritime Vessel Traffic Monitor

FastAPI backend for North Sea and Baltic vessel traffic monitoring.

## Installation

```bash
uv sync
```

## Running The Server

```bash
uv run uvicorn poseidon.main:app --reload
```

Windows helper:

```powershell
.\run.ps1
```

macOS/Linux helper:

```bash
./run.sh
```

Then open `http://localhost:8000`.

## Generating Historical Data

```bash
uv run python data_generator.py
```

This creates `data/historical_readings.csv` with 131,400 rows:
15 vessels x 365 days x 24 hourly readings for year 2025.

## API Endpoints

- `GET /` - welcome page with links.
- `GET /vessels` - authorised vessel list.
- `POST /report` - submit a telemetry reading for an existing vessel.
- `GET /map` - interactive map of all 15 vessels, coloured by latest speed risk.
- `GET /status` - health, uptime, active vessel count, report count, last update.
- `GET /history/{vessel_id}` - one-year time-series chart for one vessel.
- `GET /distribution/{year}/{month}` - 100% stacked speed-risk distribution by flag state.
- `GET /docs` - Swagger UI.

## curl Examples

Submit a reading:

```bash
curl -X POST http://localhost:8000/report \
  -H "Content-Type: application/json" \
  -d '{"vessel_id": "vessel_rotterdam_001", "readings": {"speed_knots": 18.4, "draft_m": 11.2, "heading_deg": 274, "fuel_rate_lph": 310}}'
```

Other endpoints:

```bash
curl http://localhost:8000/status
curl http://localhost:8000/vessels
curl http://localhost:8000/map
curl http://localhost:8000/history/vessel_hamburg_005
curl http://localhost:8000/distribution/2025/2
```

Unknown vessels return `403 Forbidden`. Malformed request bodies return `422 Unprocessable Entity`.

## Testing And Quality

```bash
uv run pytest
uv run ruff check src tests data_generator.py
uv run mypy src
```

## Architecture

```text
config/                 JSON server configuration and vessel whitelist
data/                   runtime JSON storage and generated historical CSV
src/poseidon/vessel.py  plain domain models, no Pydantic validation
src/poseidon/models.py  Pydantic DTOs
src/poseidon/config_loader.py  JSON loading and single-string WKT parsing
src/poseidon/data_cleaning.py  vectorised pandas cleaning and WKT extraction
src/poseidon/persistence.py    JSON and CSV persistence
src/poseidon/vessel_manager.py service layer and business rules
src/poseidon/dependencies.py   FastAPI dependency provider
src/poseidon/visualization.py  Plotly scatter_map map
src/poseidon/temporal_visualization.py  history and distribution charts
src/poseidon/main.py    FastAPI app, lifespan, routes
tests/                  pytest suite using TestClient and dependency_overrides
```

## Historical Data Note

`data_generator.py` generates synthetic AIS-style hourly telemetry using sinusoidal patterns
for speed, draft, heading, and fuel consumption. It intentionally injects a small number of
invalid speed values so the pandas cleaning pipeline has glitches to remove.
