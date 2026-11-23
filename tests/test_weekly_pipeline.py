"""Synthetic alignment fixtures only, no medical experiment or accuracy claims."""
import unittest

from ml_pipeline.weekly import weekly_features, last_available_baseline


class WeeklyPipelineTests(unittest.TestCase):
    def test_unpublished_health_is_not_a_feature_or_baseline(self):
        rows = [{'region_id':'US-FL','week_end':'2026-01-03','available_at':'2026-01-05T00:00:00Z','admissions':4},
                {'region_id':'US-FL','week_end':'2026-01-10','available_at':'2026-01-20T00:00:00Z','admissions':99}]
        result = weekly_features('US-FL','2026-01-24',rows,[])
        self.assertIsNone(result['features']['admissions_lag_2'])
        self.assertEqual(result['features']['admissions_lag_3'],4)
        self.assertFalse(result['training_approved'])
        self.assertEqual(last_available_baseline('US-FL',result['issue_time'],rows),4)

    def test_missing_availability_and_duplicate_dates_rejected(self):
        row = {'region_id':'US-FL','week_end':'2026-01-03','available_at':'2026-01-04','admissions':4}
        with self.assertRaises(ValueError):
            weekly_features('US-FL','2026-01-24',[row],[])
        row['available_at'] = '2026-01-04T00:00:00Z'
        with self.assertRaises(ValueError):
            weekly_features('US-FL','2026-01-24',[row,row],[])

    def test_other_regions_and_missing_values_never_become_zero(self):
        row = {'region_id':'OTHER','week_end':'2026-01-03','available_at':'2026-01-04T00:00:00Z','admissions':7}
        result = weekly_features('US-FL','2026-01-24',[row],[])
        self.assertTrue(result['missing_features'])
        self.assertTrue(all(value is None for value in result['features'].values()))
        self.assertIsNone(last_available_baseline('US-FL',result['issue_time'],[row]))
