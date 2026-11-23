"""Preparation primitives only; no fabricated target or training pipeline."""

from datetime import timedelta, timezone
import hashlib
from math import isfinite
from pathlib import Path


def dataset_manifest(path, source, license_id, target=None):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return {
        "filename": Path(path).name,
        "sha256": digest.hexdigest(),
        "source": source,
        "license": license_id,
        "target": target,
        "schema_version": "manifest-v1",
        "training_ready": False,
    }


def daily_lags(observations, issue_time, lags=(1, 7)):
    """UTC daily fixture/normalized observations with explicit availability timestamps.

    Does not infer availability from the event date; SQL monthly rows do not meet
    this contract. Missing lags remain null. Same-day duplicates are rejected.
    """
    if issue_time.tzinfo is None or issue_time.utcoffset() is None:
        raise ValueError("issue_time requires timezone")
    if not lags or any(
        isinstance(lag, bool) or not isinstance(lag, int) or not 1 <= lag <= 3650 for lag in lags
    ):
        raise ValueError("Invalid daily lag")
    issue_time = issue_time.astimezone(timezone.utc)
    by_day = {}
    for row in observations:
        event, available = row["event_time"], row["available_at"]
        if (
            event.tzinfo is None
            or available.tzinfo is None
            or event.utcoffset() is None
            or available.utcoffset() is None
        ):
            raise ValueError("Observation timestamps require timezone")
        if available > issue_time or event > issue_time:
            continue
        value = row["value"]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
            raise ValueError("Observation must be finite")
        day = event.astimezone(timezone.utc).date()
        if day in by_day:
            raise ValueError("Daily aggregation must be explicit before lag creation")
        by_day[day] = value
    values = {f"lag_{lag}": by_day.get(issue_time.date() - timedelta(days=lag)) for lag in lags}
    return {
        "features": values,
        "missing_lags": [key for key, value in values.items() if value is None],
        "calendar": "UTC daily",
        "target": None,
    }
