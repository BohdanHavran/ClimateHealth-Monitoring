"""Explicit weekly alignment; never infers publication time from event date."""

from datetime import date, datetime, timedelta, timezone
from math import isfinite


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("Publication timestamp must have a UTC offset")
    return result


def index_rows(rows, region):
    result = {}
    for row in rows:
        if row["region_id"] != region:
            continue
        week = date.fromisoformat(row["week_end"])
        if week.weekday() != 5 or week in result:
            raise ValueError("Expected unique Saturday week ends per region and snapshot")
        timestamp(row["available_at"])  # A global dataset update timestamp is insufficient.
        result[week] = row
    return result


def weekly_features(region, target_week_end, health, climate):
    target = date.fromisoformat(target_week_end)
    if target.weekday() != 5:
        raise ValueError("Target must be a complete Sunday-Saturday week")
    issue = datetime.combine(target - timedelta(days=6), datetime.min.time(), tzinfo=timezone.utc)
    health_index, climate_index = index_rows(health, region), index_rows(climate, region)
    features, missing = {}, []
    for prefix, rows, field, lags in (
        ("admissions", health_index, "admissions", (2, 3, 4, 5)),
        ("temperature", climate_index, "mean_temp", (1, 2, 3, 4)),
        ("humidity", climate_index, "mean_humidity", (1, 2, 3, 4)),
    ):
        for lag in lags:
            name = f"{prefix}_lag_{lag}"
            row = rows.get(target - timedelta(weeks=lag))
            value = row.get(field) if row and timestamp(row["available_at"]) <= issue else None
            if value is not None and (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not isfinite(value)
            ):
                raise ValueError("Features must be finite numeric observations")
            if value is not None and (
                (prefix == "admissions" and value < 0)
                or (prefix == "humidity" and not 0 <= value <= 100)
                or (prefix == "temperature" and not -100 <= value <= 70)
            ):
                raise ValueError("Feature outside physical/count domain")
            features[name] = value
            if value is None:
                missing.append(name)
    return {
        "region_id": region,
        "issue_time": issue.isoformat(),
        "target_week_end": target_week_end,
        "features": features,
        "missing_features": missing,
        "features_complete": not missing,
        "training_approved": False,
    }


def last_available_baseline(region, issue_time, health):
    issue = timestamp(issue_time)
    available = [
        (week, row)
        for week, row in index_rows(health, region).items()
        if week < issue.date() and timestamp(row["available_at"]) <= issue
    ]
    if not available:
        return None
    value = max(available, key=lambda item: item[0])[1].get("admissions")
    if value is None:
        return None
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not isfinite(value)
        or value < 0
    ):
        raise ValueError("Invalid baseline label")
    return value
