"""Tests for inspection only; synthetic fixtures are not medical data."""
import math
import csv
import hashlib
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
import sys

from climate_data_quality import inspect_number, validate_observation
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from profile_dataset import profile


class DataQualityTests(unittest.TestCase):
    def test_missing_invalid_and_nonfinite(self):
        for value in (None, "", "  ", "NAN", "Unknown"):
            self.assertEqual(inspect_number(value).status, "missing")
        for value in (float("nan"), float("inf"), "-Infinity"):
            self.assertEqual(inspect_number(value).status, "nonfinite")
        self.assertEqual(inspect_number("oops").status, "invalid")
        self.assertEqual(inspect_number(True).status, "invalid")

    def test_value_is_not_clipped_or_silently_changed(self):
        result = inspect_number("99999", minimum=-90, maximum=90)
        self.assertEqual(result.status, "out_of_range")
        self.assertEqual(result.value, 99999.0)

    def test_valid_timestamp_and_finite_observation(self):
        result = validate_observation({"value": 1.25, "available_at": "2026-01-01T00:00:00Z"},
                                      datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(result, [])

    def test_reject_unavailable_or_ambiguous_time(self):
        issue = datetime(2026, 1, 1, tzinfo=timezone.utc)
        for available_at in ("", "not-a-date", "2026-01-01T00:00:00", "2026-01-02T00:00:00Z"):
            self.assertTrue(validate_observation({"value": 1, "available_at": available_at}, issue))
        with self.assertRaises(ValueError):
            validate_observation({"value": 1, "available_at": "2026-01-01T00:00:00Z"}, datetime(2026, 1, 1))

    def test_empty_and_nonfinite_values_are_rejected(self):
        issue = datetime(2026, 1, 1, tzinfo=timezone.utc)
        for value in (None, "", math.inf, math.nan):
            self.assertIn("value", validate_observation({"value": value, "available_at": "2025-12-31T00:00:00Z"}, issue))

    def test_profile_checks_pairs_with_missing_values_and_preserves_source(self):
        rows = [
            {"Min_Temp (°C)": "10", "Avg_Temp (°C)": "5", "Max_Temp (°C)": "20", "Latitude": "99999", "Longitude": ""},
            {"Min_Temp (°C)": "30", "Avg_Temp (°C)": "", "Max_Temp (°C)": "20", "Latitude": "0", "Longitude": "0"},
            {"Min_Temp (°C)": "0", "Avg_Temp (°C)": "1", "Max_Temp (°C)": "2", "Latitude": "0", "Longitude": "0"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synthetic_fixture.csv"
            with path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0]))
                writer.writeheader(); writer.writerows(rows)
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            result = profile(path)
            self.assertEqual(result["temperature_adjacent_pair_violations"], 1)
            self.assertEqual(result["temperature_any_pair_violations"], 2)
            self.assertEqual(result["temperature_complete_triples"], 2)
            self.assertEqual(result["temperature_complete_triple_violations"], 1)
            self.assertEqual(result["coordinate_status_counts"]["Latitude_out_of_range"], 1)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), before)


if __name__ == "__main__":
    unittest.main()
