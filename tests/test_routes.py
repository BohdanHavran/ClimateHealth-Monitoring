"""HTTP contract tests: no external API or MySQL server is contacted."""
import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import climat


class RoutesTest(unittest.TestCase):
    def setUp(self):
        climat.app.config.update(TESTING=True)
        self.client = climat.app.test_client()

    def test_liveness_does_not_touch_database(self):
        with patch.object(climat, 'get_db', side_effect=AssertionError('DB accessed')):
            response = self.client.get('/health/live')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['status'], 'ok')

    def test_readiness_reports_database_failure_without_details(self):
        with patch.object(climat, 'get_db', side_effect=RuntimeError('sensitive detail')):
            response = self.client.get('/health/ready')
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('sensitive detail', response.get_data(as_text=True))

    def test_readiness_probes_database(self):
        connection = MagicMock()
        with patch.object(climat, 'get_db', return_value=connection):
            response = self.client.get('/health/ready')
        self.assertEqual(response.status_code, 200)
        connection.cursor.return_value.__enter__.return_value.execute.assert_called_once_with('SELECT 1')

    def test_invalid_analysis_inputs_rejected_before_database(self):
        cases = [
            {'mode': 'unknown'},
            {'mode': 'manual', 'criteria': 'invalid'},
            {'mode': 'manual', 'manual_temp': 'NaN'},
            {'mode': 'manual', 'manual_temp': 'inf'},
            {'mode': 'manual', 'manual_humidity': '101'},
            {'mode': 'manual', 'manual_solar': '-1'},
            {'mode': 'db', 'year': '2024', 'month': '13'},
            {'mode': 'api', 'api_city': '   '},
        ]
        for data in cases:
            with self.subTest(data=data), patch.object(climat, 'get_db', side_effect=AssertionError('DB accessed')):
                self.assertEqual(self.client.post('/api/analyze', data=data).status_code, 400)

    def test_valid_manual_analysis_contract(self):
        with patch.object(climat, 'get_hri_impact', return_value=('impact', 'recommendations', 'diseases')):
            response = self.client.post('/api/analyze', data={'mode':'manual', 'manual_temp':'20', 'manual_solar':'180', 'manual_humidity':'65'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('hri', response.get_json()['results'][0])

    def test_invalid_coordinates_and_limits_are_rejected_before_database(self):
        urls = ['/api/hri_at?lat=NaN&lon=0', '/api/hri_at?lat=91&lon=0',
                '/api/places_in_bounds?minLat=2&maxLat=1&minLon=0&maxLon=1',
                '/api/places_in_bounds?minLat=0&maxLat=1&minLon=0&maxLon=1&limit=500000',
                '/api/places_in_bounds?minLat=0&maxLat=inf&minLon=0&maxLon=1']
        for url in urls:
            with self.subTest(url=url), patch.object(climat, 'get_db', side_effect=AssertionError('DB accessed')):
                self.assertEqual(self.client.get(url).status_code, 400)

    def test_analysis_database_error_is_redacted_and_not_masked_by_rollback(self):
        with patch.object(climat, 'get_cursor', side_effect=RuntimeError('sensitive detail')):
            response = self.client.post('/api/analyze', data={'mode':'db','year':'2024'})
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('sensitive detail', response.get_data(as_text=True))

    def test_nonfinite_cached_data_is_unavailable(self):
        cached = {'avg_temp': 20.0, 'solar': 180.0, 'humidity': 65.0, 'hri': 0.5}
        for field in cached:
            with self.subTest(field=field):
                bad = dict(cached, **{field: float('nan')})
                with patch.object(climat, 'get_cached_hri', return_value=bad), \
                     patch.object(climat, 'get_hri_impact', side_effect=AssertionError('invalid cache used')):
                    response = self.client.get('/api/hri_at?lat=49&lon=24')
                self.assertEqual(response.status_code, 503)
                self.assertNotIn('NaN', response.get_data(as_text=True))

    def test_valid_cached_result_remains_compatible(self):
        cached = {'avg_temp': 20.0, 'solar': 180.0, 'humidity': 65.0, 'hri': 0.5}
        with patch.object(climat, 'get_cached_hri', return_value=cached), \
             patch.object(climat, 'get_hri_impact', return_value=('a', 'b', 'c')), \
             patch.object(climat, 'get_current_weather_by_coords', side_effect=AssertionError('cache missed')):
            response = self.client.get('/api/hri_at?lat=49&lon=24')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()['cached'])
        self.assertEqual(response.get_json()['hri'], 0.5)

    def test_password_file_takes_precedence_and_has_a_size_limit(self):
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / 'secret'
            path.write_text('file-password\n', encoding='utf-8')  # pragma: allowlist secret -- synthetic fixture
            with patch.dict(os.environ, {'DB_PASS_FILE': str(path), 'DB_PASS':'env-password'}):  # pragma: allowlist secret -- synthetic fixture
                self.assertEqual(climat.get_db_password(), 'file-password')
                path.write_bytes(b'x' * 4097)
                with self.assertRaises(ValueError):
                    climat.get_db_password()

    def test_missing_secret_is_rejected_without_fallback(self):
        with patch.dict(os.environ, {'DB_PASS_FILE':'', 'DB_PASS':''}):
            with self.assertRaises(ValueError):
                climat.get_db_password()

    def test_missing_secret_file_fails_closed_without_leaking_path(self):
        with patch.dict(os.environ, {'DB_PASS_FILE':'nonexistent-secret', 'DB_PASS':'fallback'}):  # pragma: allowlist secret -- synthetic fixture
            with self.assertRaises(ValueError) as exc:
                climat.get_db_password()
        self.assertNotIn('nonexistent-secret', str(exc.exception))

    def test_mysql_connection_uses_bounded_timeouts_and_selected_port(self):
        with (
            climat.app.app_context(),
            patch.dict(os.environ, {'DB_PASS_FILE':'', 'DB_PASS':'temporary', 'DB_PORT':'3307'}),  # pragma: allowlist secret -- synthetic fixture
            patch.object(climat.pymysql, 'connect') as connect,
        ):
            climat.get_db()
            kwargs = connect.call_args.kwargs
            self.assertEqual(kwargs['port'], 3307)
            self.assertEqual((kwargs['connect_timeout'], kwargs['read_timeout'], kwargs['write_timeout']), (3, 5, 5))


if __name__ == '__main__':
    unittest.main()
