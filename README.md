# Poseidon — Maritime Vessel Traffic Monitor

Poseidon is a Python-based maritime vessel traffic monitoring and analytics
application focused on vessel activity in the North Sea and Baltic Sea.

The project processes vessel telemetry, validates and cleans incoming data,
stores historical readings, exposes the data through a FastAPI REST API,
and provides interactive Plotly visualizations for vessel monitoring and
historical analysis.


## Features

- REST API built with FastAPI
- Vessel telemetry submission and validation
- Authorized vessel management
- Historical vessel data generation
- Data cleaning and processing with Pandas
- JSON and CSV data persistence
- Interactive vessel map with Plotly
- Historical vessel time-series visualization
- Speed-risk distribution visualization
- Application status and monitoring endpoint
- Automated tests with pytest
- Static type checking with mypy
- Code quality checks with Ruff

## Technologies

- Python 3.13
- FastAPI
- Pandas
- Pydantic
- Plotly
- PyArrow
- Uvicorn
- pytest
- mypy
- Ruff
- uv

## Project Structure

```text
Poseidon/
├── config/
│   ├── server_config.json
│   └── vessels.json
├── data/
│   ├── historical_readings.csv
│   └── readings.json
├── src/
│   └── poseidon/
│       ├── config_loader.py
│       ├── data_cleaning.py
│       ├── dependencies.py
│       ├── main.py
│       ├── models.py
│       ├── persistence.py
│       ├── temporal_visualization.py
│       ├── vessel.py
│       ├── vessel_manager.py
│       └── visualization.py
├── tests/
├── data_generator.py
├── pyproject.toml
├── run.ps1
├── run.sh
└── README.md
```

## Installation

Poseidon uses `uv` for dependency management.

Install the project dependencies with:

```bash
uv sync
```

## Running the Application

Start the server with:

```bash
uv run uvicorn poseidon.main:app --reload
```

On Windows, you can also use:

```powershell
.\run.ps1
```

On macOS/Linux:

```bash
./run.sh
```

The application will be available at:

```text
http://localhost:8000
```

FastAPI's interactive Swagger documentation is available at:

```text
http://localhost:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Welcome page |
| GET | `/vessels` | List authorized vessels |
| POST | `/report` | Submit a telemetry reading for an existing vessel |
| GET | `/map` | Display the interactive vessel map |
| GET | `/status` | Display application status information |
| GET | `/history/{vessel_id}` | Display historical data for a vessel |
| GET | `/distribution/{year}/{month}` | Display monthly speed-risk distribution by flag state |
| GET | `/docs` | Swagger API documentation |

## Example Telemetry Request

A vessel telemetry reading can be submitted using:

```bash
curl -X POST http://localhost:8000/report \
  -H "Content-Type: application/json" \
  -d '{
    "vessel_id": "vessel_rotterdam_001",
    "readings": {
      "speed_knots": 18.4,
      "draft_m": 11.2,
      "heading_deg": 274,
      "fuel_rate_lph": 310
    }
  }'
```

## Historical Data

The project includes a data generator for creating synthetic vessel telemetry:

```bash
uv run python data_generator.py
```

The generator creates hourly readings for 15 vessels over 365 days for the year 2025.

The generated data includes:

- Vessel speed
- Draft
- Heading
- Fuel consumption

The generated dataset is used by the application for historical analysis and visualization.

## Data Processing

Pandas is used to clean and process historical vessel data.

The project includes functionality for filtering invalid readings, extracting location information, processing historical telemetry, and preparing data for visualization.

## Testing

Run the test suite with:

```bash
uv run pytest
```

The tests cover components of the application including API endpoints, configuration loading, data cleaning, persistence, vessel management, and visualization.

## Code Quality

Run Ruff:

```bash
uv run ruff check src tests data_generator.py
```

Run mypy:

```bash
uv run mypy src
```

## Architecture

The application is separated into modules with different responsibilities:

- `main.py` — FastAPI application and API routes
- `models.py` — Pydantic request and response models
- `vessel.py` — vessel domain models
- `vessel_manager.py` — vessel management and application logic
- `data_cleaning.py` — Pandas-based data cleaning
- `persistence.py` — JSON and CSV persistence
- `config_loader.py` — configuration loading
- `dependencies.py` — FastAPI dependencies
- `visualization.py` — interactive vessel map
- `temporal_visualization.py` — historical and distribution visualizations
- `data_generator.py` — synthetic historical data generation

## About

Poseidon was developed as a Python application for working with vessel telemetry, data processing, REST APIs, automated testing, and interactive data visualization.
