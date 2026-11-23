"""Integration prototype: validate a request and report unavailable, no model.

This is not an HTTP endpoint, authentication layer, trusted ingestion service,
or clinical tool. Caller must establish provenance and authorization separately.
"""

from datetime import datetime, timezone
from math import isfinite
import re


class ContractError(ValueError):
    """The request fails the proposed contract."""


def _object(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ContractError(f"{label}: missing or unknown fields")


def _text(value, maximum, label):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ContractError(f"{label}: invalid text")


def _timestamp(value, label):
    # Restrict to the RFC3339 form used in the proposed OpenAPI schema.
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})", value
    ):
        raise ContractError(f"{label}: expected timestamp with UTC offset")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ContractError(f"{label}: invalid timestamp") from error
    if result.tzinfo is None or result.utcoffset() is None:
        raise ContractError(f"{label}: timezone required")
    return result


def evaluate_unavailable_request(request, clock=None):
    """Check structural validity and return an explicit model-unavailable result.

    Feature names, claimed timestamps and sources are not trusted provenance;
    authorization, allowed feature definitions and schema compatibility require
    a future authenticated service and real data contracts.
    """
    _object(
        request,
        {"region_id", "issue_time", "horizon_days", "feature_schema_version", "features"},
        "request",
    )
    _text(request["region_id"], 128, "region_id")
    _text(request["feature_schema_version"], 64, "feature_schema_version")
    issue = _timestamp(request["issue_time"], "issue_time")
    horizon = request["horizon_days"]
    if isinstance(horizon, bool) or not isinstance(horizon, int) or not 1 <= horizon <= 30:
        raise ContractError("horizon_days: expected integer from 1 to 30")
    features = request["features"]
    if not isinstance(features, list) or not 1 <= len(features) <= 512:
        raise ContractError("features: expected 1 to 512 features")
    names = set()
    for feature in features:
        _object(
            feature, {"name", "value", "unit", "event_time", "available_at", "source"}, "feature"
        )
        for field, maximum in (("name", 128), ("unit", 64), ("source", 128)):
            _text(feature[field], maximum, field)
        if feature["name"] in names:
            raise ContractError("features: duplicate name")
        names.add(feature["name"])
        value = feature["value"]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ContractError("value: expected finite JSON number")
        try:
            finite = isfinite(value)
        except OverflowError:
            finite = False
        if not finite:
            raise ContractError("value: expected finite JSON number")
        _timestamp(feature["event_time"], "event_time")
        if _timestamp(feature["available_at"], "available_at") > issue:
            raise ContractError("available_at: feature unavailable at issue time")
    issued = clock if clock is not None else datetime.now(timezone.utc)
    if not isinstance(issued, datetime) or issued.tzinfo is None or issued.utcoffset() is None:
        raise ValueError("clock must be timezone-aware")
    return {
        "status": "unavailable",
        "target": None,
        "value": None,
        "unit": None,
        "model_version": None,
        "issued_at": issued.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "data_quality": "unavailable",
        "reason": "model_unavailable",
    }
