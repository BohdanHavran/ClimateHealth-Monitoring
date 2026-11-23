"""Synthetic preparation tests; not a real medical experiment."""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import tempfile
import unittest

from climate_health.datasets import daily_lags, dataset_manifest


class DatasetTests(unittest.TestCase):
    def test_manifest_tracks_bytes_without_claiming_training_readiness(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'synthetic.csv'
            path.write_text('synthetic\n1\n')
            first = dataset_manifest(path,'synthetic-fixture','test-only')
            path.write_text('synthetic\n2\n')
            self.assertNotEqual(first['sha256'],dataset_manifest(path,'synthetic-fixture','test-only')['sha256'])
            self.assertFalse(first['training_ready'])
            self.assertIsNone(first['target'])

    def test_lags_exclude_unpublished_values_and_preserve_missing(self):
        issue = datetime(2026,1,10,tzinfo=timezone.utc)
        rows = [{'event_time':issue-timedelta(days=1),'available_at':issue-timedelta(hours=1),'value':2},
                {'event_time':issue-timedelta(days=7),'available_at':issue+timedelta(days=1),'value':99}]
        result = daily_lags(rows,issue)
        self.assertEqual(result['features'],{'lag_1':2,'lag_7':None})
        self.assertEqual(result['missing_lags'],['lag_7'])

    def test_ambiguous_time_and_duplicate_days_rejected(self):
        with self.assertRaises(ValueError):
            daily_lags([],datetime(2026,1,10))
        issue = datetime(2026,1,10,tzinfo=timezone.utc)
        row = {'event_time':issue-timedelta(days=1),'available_at':issue,'value':2}
        with self.assertRaises(ValueError):
            daily_lags([row,row],issue)
