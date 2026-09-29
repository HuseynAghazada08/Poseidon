from __future__ import annotations

import logging
from collections.abc import Mapping

import pandas as pd

logger = logging.getLogger(__name__)

_WKT_PATTERN = r"POINT\s*\((?P<lon>-?\d+\.?\d*)\s+(?P<lat>-?\d+\.?\d*)\)"

RISK_BANDS = ["Safe", "Moderate", "Unsafe", "Danger"]
RISK_COLOURS = {
    "Safe": "green",
    "Moderate": "yellow",
    "Unsafe": "orange",
    "Danger": "red",
    "No data": "black",
}


class DataCleaner:
    @staticmethod
    def validate_report(readings: Mapping[str, object]) -> tuple[bool, list[str]]:
        errors: list[str] = []
        for key in ("speed_knots", "draft_m", "heading_deg", "fuel_rate_lph"):
            if key in readings:
                val = readings[key]
                if not isinstance(val, (int, float)):
                    errors.append(f"{key} must be numeric")
        if "speed_knots" in readings and isinstance(readings["speed_knots"], (int, float)):
            if readings["speed_knots"] < 0:
                errors.append("speed_knots cannot be negative")
        if "heading_deg" in readings and isinstance(readings["heading_deg"], (int, float)):
            h = readings["heading_deg"]
            if not (0 <= h < 360):
                errors.append("heading_deg must be in [0, 360)")
        return len(errors) == 0, errors

    @staticmethod
    def clean_historical_batch(df: pd.DataFrame) -> pd.DataFrame:
        initial = len(df)

        cleaned = (
            df.dropna(subset=["vessel_id", "timestamp"])
            .loc[lambda d: d["speed_knots"].between(0, 50)]
            .loc[lambda d: (d["draft_m"] >= 0) & (d["fuel_rate_lph"] >= 0)]
            .loc[lambda d: d["heading_deg"].between(0, 360, inclusive="left")]
            .assign(timestamp=lambda d: pd.to_datetime(d["timestamp"], utc=True))
        )

        dropped = initial - len(cleaned)
        pct = dropped / initial * 100 if initial > 0 else 0.0
        logger.info(
            "Historical clean: %d rows loaded, %d dropped (%.2f%%)",
            initial,
            dropped,
            pct,
        )
        return cleaned

    @staticmethod
    def parse_wkt_column(series: pd.Series[str]) -> pd.DataFrame:
        coords: pd.DataFrame = series.str.extract(_WKT_PATTERN)
        return coords.astype(float)

    @staticmethod
    def categorise_by_speed(df: pd.DataFrame, thresholds: dict[str, float]) -> pd.DataFrame:
        safe = thresholds["speed_safe"]
        moderate = thresholds["speed_moderate"]
        danger = thresholds["speed_danger"]
        bins = [-float("inf"), safe, moderate, danger, float("inf")]
        labels = ["Safe", "Moderate", "Unsafe", "Danger"]
        df = df.copy()
        df["risk_band"] = pd.cut(
            df["speed_knots"],
            bins=bins,
            labels=labels,
            right=True,
        )
        return df

    @staticmethod
    def distribution_by_flag(
        df: pd.DataFrame,
        thresholds: dict[str, float],
        year: int,
        month: int,
    ) -> pd.DataFrame:
        subset = df.loc[(df["timestamp"].dt.year == year) & (df["timestamp"].dt.month == month)]
        if subset.empty:
            return pd.DataFrame()

        subset = DataCleaner.categorise_by_speed(subset, thresholds)

        counts = (
            subset.groupby(["flag_state", "risk_band"], observed=True)
            .agg(count=("vessel_id", "size"))
            .reset_index()
        )
        totals = counts.groupby("flag_state")["count"].transform("sum")
        counts["percentage"] = counts["count"] / totals * 100
        return counts
