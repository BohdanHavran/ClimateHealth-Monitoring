"""Synthetic provider/DB fixtures; no external requests or MySQL writes."""
from datetime import datetime,timezone
import unittest
from unittest.mock import MagicMock,patch

from flask import Flask
import requests
from pathlib import Path
import yaml
import jsonschema

from climate_health.api import create_api
from climate_health.open_meteo import OpenMeteoProvider
from climate_health.repository import ClimateRepository


def payload():
    return {'current_units':{'temperature_2m':'°C','relative_humidity_2m':'%','shortwave_radiation':'W/m²'},
            'current':{'time':datetime.now(timezone.utc).isoformat(),'temperature_2m':4,
                       'relative_humidity_2m':70,'shortwave_radiation':0}}


class MonitoringTests(unittest.TestCase):
    def setUp(self):
        self.connection = MagicMock()
        self.connect = MagicMock(return_value=self.connection)
        app = Flask(__name__); app.register_blueprint(create_api(self.connect))
        self.client = app.test_client()

    def test_search_is_bounded_and_parameterized(self):
        cursor = self.connection.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = []
        result = self.client.get('/api/v1/places/search?q=Lviv&limit=3')
        self.assertEqual(result.status_code,200)
        sql,params = cursor.execute.call_args.args
        self.assertTrue(sql.startswith('SELECT '))
        self.assertNotIn('Lviv',sql)
        self.assertEqual(params,('%Lviv%','%Lviv%',3))
        ClimateRepository(self.connection).search_places('a%_=',3)
        self.assertEqual(cursor.execute.call_args.args[1][0],'%a=%=_==%')

    def test_invalid_search_and_coordinates_never_call_db(self):
        for path in ('places/search?q=a','places/search?q=Lviv&limit=21',
                     'weather?lat=NaN&lon=24','weather?lat=49','weather?lat=49&lon=24&city=Lviv'):
            self.assertEqual(self.client.get('/api/v1/'+path).status_code,400)
        self.connect.assert_not_called()

    def test_weather_api_real_contract_without_database(self):
        with patch.object(OpenMeteoProvider,'coordinates',return_value={'source':'Open-Meteo','solar':0}):
            result = self.client.get('/api/v1/weather?lat=49&lon=24')
        self.assertEqual(result.status_code,200)
        self.assertEqual(result.json['meta']['license'],'CC-BY-4.0')
        self.assertIn('received_at',result.json['meta'])
        self.connect.assert_not_called()

    def test_invalid_source_and_timeout_are_503_not_bad_user_input(self):
        for error in (ValueError('private source detail'),requests.Timeout()):
            with patch.object(OpenMeteoProvider,'coordinates',side_effect=error):
                result = self.client.get('/api/v1/weather?lat=49&lon=24')
                self.assertEqual(result.status_code,503)
                self.assertNotIn('private source detail',result.get_data(as_text=True))

    def test_provider_units_timestamps_cache_and_no_imputation(self):
        response = MagicMock(status_code=200)
        response.json.side_effect = lambda:payload()
        transport = MagicMock(return_value=response)
        provider = OpenMeteoProvider(transport=transport)
        first = provider.coordinates(49,24)
        second = provider.coordinates(49,24)
        self.assertEqual(first['solar'],0)
        self.assertEqual(first['solar_method'],'model_shortwave_radiation')
        self.assertTrue(second['cached']); self.assertFalse(first['cached'])
        self.assertEqual(first['fetched_at'],second['fetched_at'])
        self.assertEqual(transport.call_count,1)
        self.assertFalse(transport.call_args.kwargs['allow_redirects'])
        self.assertIn('shortwave_radiation',transport.call_args.kwargs['params']['current'])
        schema = yaml.safe_load((Path(__file__).resolve().parents[1]/'docs/api/backend.openapi.yaml').read_text(encoding='utf8'))
        jsonschema.validate(first,schema['components']['schemas']['CurrentWeather'])

    def test_missing_invalid_and_unexpected_units_never_cached(self):
        for bad in ('missing','nonfinite','units'):
            body = payload()
            if bad=='missing': del body['current']['shortwave_radiation']
            elif bad=='nonfinite': body['current']['temperature_2m']=float('nan')
            else: body['current_units']['temperature_2m']='F'
            response = MagicMock(status_code=200); response.json.return_value=body
            provider = OpenMeteoProvider(transport=MagicMock(return_value=response))
            with self.assertRaises((RuntimeError,ValueError,KeyError)):
                provider.coordinates(49,24)
            self.assertFalse(provider.cache)

    def test_daily_quota_applies_before_network(self):
        transport = MagicMock()
        provider = OpenMeteoProvider(transport=transport)
        provider.daily_quota.limit = 0
        with self.assertRaises(RuntimeError): provider.coordinates(49,24)
        transport.assert_not_called()
