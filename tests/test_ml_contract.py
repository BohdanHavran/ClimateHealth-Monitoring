"""Synthetic contract checks: no medical samples or trained model."""
import unittest
from copy import deepcopy
from datetime import datetime, timezone

from ml_contract import ContractError, evaluate_unavailable_request


def fixture():
    return {
        "region_id": "synthetic-region",
        "issue_time": "2026-01-01T12:00:00Z",
        "horizon_days": 1,
        "feature_schema_version": "synthetic-v1",
        "features": [{
            "name": "temperature", "value": 3.4, "unit": "C",
            "event_time": "2026-01-01T00:00:00Z",
            "available_at": "2026-01-01T01:00:00Z", "source": "synthetic-fixture",
        }],
    }


class ContractTests(unittest.TestCase):
    def test_no_model_never_returns_zero_or_prediction(self):
        result = evaluate_unavailable_request(fixture(), datetime(2026, 1, 1, 12, tzinfo=timezone.utc))
        self.assertEqual(result["status"], "unavailable")
        self.assertIsNone(result["value"])
        self.assertIsNone(result["model_version"])
        self.assertEqual(result["reason"], "model_unavailable")

    def test_time_leak_and_ambiguous_dates_rejected(self):
        for issue, available in (("2026-01-01T12:00:00Z", "2026-01-02T00:00:00Z"),
                                 ("2026-01-01T12:00:00", "2026-01-01T00:00:00Z"),
                                 ("2026-01-01T12:00:00Z", "not-a-date")):
            request = fixture(); request["issue_time"] = issue
            request["features"][0]["available_at"] = available
            with self.assertRaises(ContractError):
                evaluate_unavailable_request(request)

    def test_nonfinite_invalid_feature_and_duplicate_rejected(self):
        for value in (None, True, "1", float("nan"), float("inf"), float("-inf")):
            request = fixture(); request["features"][0]["value"] = value
            with self.assertRaises(ContractError):
                evaluate_unavailable_request(request)
        request = fixture(); request["features"].append(deepcopy(request["features"][0]))
        with self.assertRaises(ContractError):
            evaluate_unavailable_request(request)

    def test_unknown_fields_and_missing_features_rejected(self):
        for key, value in (("unknown", "value"), ("features", []), ("horizon_days", True), ("horizon_days", 31)):
            request = fixture(); request[key] = value
            with self.assertRaises(ContractError):
                evaluate_unavailable_request(request)

    def test_iso_timestamp_requires_event_timezone(self):
        request = fixture(); request["features"][0]["event_time"] = "2026-01-01T00:00:00"
        with self.assertRaises(ContractError):
            evaluate_unavailable_request(request)


if __name__ == "__main__":
    unittest.main()
