"""Generate one year of hourly synthetic AIS telemetry for 15 vessels."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

VESSEL_IDS = [
    ("vessel_rotterdam_001", "Netherlands"),
    ("vessel_amsterdam_002", "Netherlands"),
    ("vessel_vlissingen_003", "Netherlands"),
    ("vessel_denhelder_004", "Netherlands"),
    ("vessel_hamburg_005", "Germany"),
    ("vessel_bremen_006", "Germany"),
    ("vessel_kiel_007", "Germany"),
    ("vessel_rostock_008", "Germany"),
    ("vessel_gdansk_009", "Poland"),
    ("vessel_gdynia_010", "Poland"),
    ("vessel_szczecin_011", "Poland"),
    ("vessel_copenhagen_012", "Denmark"),
    ("vessel_aarhus_013", "Denmark"),
    ("vessel_esbjerg_014", "Denmark"),
    ("vessel_frederikshavn_015", "Denmark"),
]


def generate(output_path: str = "data/historical_readings.csv", year: int = 2025) -> None:
    rng = np.random.default_rng(42)
    timestamps = pd.date_range(
        start=f"{year}-01-01 00:00:00",
        end=f"{year}-12-31 23:00:00",
        freq="h",
        tz="UTC",
    )
    n_hours = len(timestamps)

    rows = []
    for vessel_id, flag_state in VESSEL_IDS:
        phase = rng.uniform(0, 2 * np.pi)
        base_speed = rng.uniform(8.0, 18.0)
        speed = base_speed + 6 * np.sin(np.linspace(0, 40 * np.pi, n_hours) + phase)
        speed = np.clip(speed, 0.5, 30.0)

        draft = 7.0 + 3.0 * np.sin(np.linspace(0, 8 * np.pi, n_hours) + phase)
        draft = np.clip(draft, 3.0, 13.0)

        heading = (200 + 160 * np.sin(np.linspace(0, 20 * np.pi, n_hours) + phase)) % 360

        fuel = speed * 15 + rng.normal(0, 10, n_hours)
        fuel = np.clip(fuel, 20.0, 600.0)

        glitch_idx = rng.choice(n_hours, size=int(n_hours * 0.001), replace=False)
        speed[glitch_idx] = rng.choice([-5.0, 60.0, np.nan], size=len(glitch_idx))

        for i in range(n_hours):
            rows.append(
                {
                    "vessel_id": vessel_id,
                    "flag_state": flag_state,
                    "timestamp": timestamps[i],
                    "speed_knots": float(speed[i]) if not np.isnan(speed[i]) else None,
                    "draft_m": float(draft[i]),
                    "heading_deg": float(heading[i]),
                    "fuel_rate_lph": float(fuel[i]),
                }
            )

    df = pd.DataFrame(rows)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(str(out), index=False)
    print(f"Generated {len(df):,} rows -> {out}")


if __name__ == "__main__":
    generate()
