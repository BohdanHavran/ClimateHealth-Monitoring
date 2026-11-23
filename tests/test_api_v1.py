"""Safe contract tests; all observations and credentials are synthetic fixtures."""
import ast
import os
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

from flask import Flask

from climate_health.api import create_api
from climate_health.repository import ClimateRepository, schema_report, EXPECTED_COLUMNS
from climate_health.rate_limit import WindowLimiter
from climate_health.services import analyze_hri
from climate_health.weather import CachedWeatherProvider
import climat


class APITests(unittest.TestCase):
    def setUp(self):
        self.connection = MagicMock()
        self.connect = MagicMock(return_value=self.connection)
        self.app = Flask(__name__)
        self.app.register_blueprint(create_api(self.connect))
        self.client = self.app.test_client()

    def test_status_without_database(self):
        self.assertEqual(self.client.get('/api/v1/status').status_code, 200)
        self.connect.assert_not_called()

    def test_unknown_versioned_route_has_json_error(self):
        response = climat.app.test_client().get('/api/v1/unknown')
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json['error']['code'],'http_error')

    def test_api_rate_limit_returns_retry_header(self):
        for _ in range(60):
            self.assertEqual(self.client.get('/api/v1/status').status_code,200)
        result = self.client.get('/api/v1/status')
        self.assertEqual(result.status_code,429)
        self.assertEqual(result.headers['Retry-After'],'60')

    def test_legacy_expensive_request_limit_covers_manual_analysis(self):
        with patch.object(climat,'legacy_weather_limiter',WindowLimiter(0,60)):
            result = climat.app.test_client().post('/api/analyze',data={'mode':'manual'})
        self.assertEqual(result.status_code,429)

    def test_invalid_pagination_bounds_and_json(self):
        for path in ('/observations?limit=201', '/observations?limit=NaN', '/observations?month=13',
                     '/observations?after_id=-1', '/places?south=91&north=92&west=0&east=1'):
            result = self.client.get('/api/v1' + path)
            self.assertEqual(result.status_code, 400)
            self.assertIn('code', result.json['error'])
        self.assertEqual(self.client.post('/api/v1/hri', json={'avg_temp': True}).status_code, 400)
        self.assertEqual(self.client.post('/api/v1/hri', data='bad', content_type='application/json').status_code, 400)
        self.connect.assert_not_called()

    def test_observations_cursor_and_quality_no_imputation(self):
        cursor = self.connection.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = [dict(id=i,year=2026,month=1,avg_temp=None,
                                             solar_irradiance=180,humidity=200) for i in (1,2)]
        result = self.client.get('/api/v1/observations?limit=1&year=2026')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json['meta']['next_after_id'], 1)
        self.assertIsNone(result.json['data'][0]['avg_temp'])
        self.assertIsNone(result.json['data'][0]['humidity'])
        self.assertIn('humidity:invalid', result.json['data'][0]['quality_issues'])
        sql, params = cursor.execute.call_args.args
        self.assertTrue(sql.startswith('SELECT '))
        self.assertEqual(params, (0,2026,2))

    def test_empty_and_dependency_error(self):
        self.connection.cursor.return_value.__enter__.return_value.fetchall.return_value = []
        result = self.client.get('/api/v1/observations')
        self.assertEqual(result.json['data'], [])
        self.connect.side_effect = RuntimeError('private details')
        result = self.client.get('/api/v1/observations')
        self.assertEqual(result.status_code, 503)
        self.assertNotIn('private details', result.get_data(as_text=True))

    def test_hri_pure_no_db_and_not_medical(self):
        result = self.client.post('/api/v1/hri', json={'avg_temp':20, 'solar':180, 'humidity':65})
        self.assertEqual(result.status_code, 200)
        self.assertFalse(result.json['data']['medical_prediction'])
        self.connect.assert_not_called()
        self.assertEqual(len(list(climat.build_fis_system().rules)), 27)

    def test_schema_missing_and_compatible(self):
        cursor = self.connection.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = []
        self.assertFalse(schema_report(self.connection)['compatible'])
        cursor.fetchall.return_value = [(table,col) for table, cols in EXPECTED_COLUMNS.items() for col in cols]
        self.assertTrue(schema_report(self.connection)['compatible'])

    def test_legacy_reads_have_no_ddl_or_commit(self):
        cursor = MagicMock()
        cursor.fetchone.return_value = None
        cursor.fetchall.return_value = []
        with climat.app.test_request_context(), patch.object(climat, 'get_cursor', return_value=cursor), patch.object(climat, 'commit', side_effect=AssertionError('write')):
            climat.get_hri_impact(.5)
            climat.get_cached_hri(49,24)
            for call in cursor.execute.call_args_list:
                self.assertTrue(call.args[0].lstrip().startswith('SELECT '))
        tree = ast.parse(Path(climat.__file__).read_text(encoding='utf8'))
        self.assertFalse(any(isinstance(n,ast.Constant) and isinstance(n.value,str) and n.value.lstrip().upper().startswith('CREATE TABLE') for n in ast.walk(tree)))

    def test_writes_disabled_and_connections_read_only(self):
        with climat.app.app_context(), patch.dict(os.environ, {'DB_PASS':'synthetic-fixture','DB_PASS_FILE':''}), patch.object(climat.pymysql, 'connect') as connect:  # pragma: allowlist secret -- synthetic fixture
            climat.get_db()
            connect.return_value.cursor.return_value.__enter__.return_value.execute.assert_called_once_with('START TRANSACTION READ ONLY')
            with self.assertRaises(PermissionError):
                climat.commit()
            with self.assertRaises(PermissionError):
                climat.seed_hri_impacts()
            self.assertFalse(climat.put_cached_hri(1,2,20,180,65,.5))

    def test_rate_limits_have_bounded_memory_and_reset(self):
        clock = [0]
        limiter = WindowLimiter(2,60,capacity=2,clock=lambda:clock[0])
        self.assertTrue(limiter.allow('a')); self.assertTrue(limiter.allow('a'))
        self.assertFalse(limiter.allow('a'))
        clock[0] = 60
        self.assertTrue(limiter.allow('a'))
        limiter.allow('b'); limiter.allow('c')
        self.assertEqual(len(limiter.entries),2)

    def test_weather_cache_and_global_quota(self):
        response = MagicMock(status_code=200)
        response.json.return_value = {'main':{'temp':20,'humidity':60},'clouds':{'all':40}}
        transport = MagicMock(return_value=response)
        clock = [0]
        weather = CachedWeatherProvider(lambda:'synthetic-fixture',clock=lambda:clock[0],transport=transport)
        self.assertEqual(weather.city('Lviv'),weather.city('lviv'))
        self.assertEqual(transport.call_count,1)
        clock[0] = 301
        weather.city('Lviv')
        self.assertEqual(transport.call_count,2)
        weather.quota.limit = 0
        with self.assertRaises(RuntimeError):
            weather.city('Other')


if __name__ == '__main__':
    unittest.main()
