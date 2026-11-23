"""Read-only primitive checks for data ingestion; this is not a medical model."""

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Any, Optional


@dataclass(frozen=True)
class NumberInspection:
    status: str
    value: Optional[float] = None


def inspect_number(
    raw: Any, minimum: Optional[float] = None, maximum: Optional[float] = None
) -> NumberInspection:
    """Inspect numeric input without filling, clipping, or modifying it."""
    if raw is None:
        return NumberInspection("missing")
    if isinstance(raw, bool):
        return NumberInspection("invalid")
    if isinstance(raw, str) and raw.strip().lower() in {"", "nan", "unknown"}:
        return NumberInspection("missing")
    try:
        value = float(raw)
    except (TypeError, ValueError, OverflowError):
        return NumberInspection("invalid")
    if not isfinite(value):
        return NumberInspection("nonfinite")
    if (minimum is not None and value < minimum) or (maximum is not None and value > maximum):
        return NumberInspection("out_of_range", value)
    return NumberInspection("valid", value)


def validate_observation(observation: dict, issue_time: datetime) -> list[str]:
    """Return invalid fields for an individual feature at an aware issue time.

    This is a narrow primitive, not full schema, provenance or authorization
    validation. Missing or malformed availability must never be treated as old.
    """
    if issue_time.tzinfo is None or issue_time.utcoffset() is None:
        raise ValueError("issue_time must include a timezone")
    errors = []
    if inspect_number(observation.get("value")).status != "valid":
        errors.append("value")
    try:
        value = observation.get("available_at")
        if not isinstance(value, str):
            raise ValueError("available_at must be an ISO timestamp")
        available = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if available.tzinfo is None or available.utcoffset() is None:
            raise ValueError("timezone missing")
        if available > issue_time:
            raise ValueError("feature unavailable at issue time")
    except (ValueError, TypeError, OverflowError):
        errors.append("available_at")
    return errors
