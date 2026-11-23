"""Synthetic contract fixtures; no medical data, trained artifacts, or real tokens."""
from copy import deepcopy
import os
import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
import requests

from climate_health.ml_client import MLClient
from ml_service.app import app
from ml_contract import evaluate_unavailable_request


def fixture():
    return {'region_id':'synthetic-region', 'issue_time':'2026-01-01T12:00:00Z',
            'horizon_days':1, 'feature_schema_version':'climate-v1',
            'features':[{'name':'temperature','value':3.4,'unit':'C',
                         'event_time':'2026-01-01T00:00:00Z',
                         'available_at':'2026-01-01T01:00:00Z','source':'synthetic-fixture'}]}


class MLHTTPTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.headers = {'Authorization':'Bearer synthetic-test-only'}
        self.env = patch.dict(os.environ, {'ML_SERVICE_TOKEN':'synthetic-test-only'})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_service_authentication_and_health(self):
        self.assertEqual(self.client.get('/health/live').status_code,200)
        self.assertEqual(self.client.post('/api/v1/predict',json=fixture()).status_code,401)
        with patch.dict(os.environ, {'ML_SERVICE_TOKEN':''}):
            self.assertEqual(self.client.post('/api/v1/predict',json=fixture(),headers=self.headers).status_code,401)

    def test_service_honest_unavailable(self):
        result = self.client.post('/api/v1/predict',json=fixture(),headers=self.headers)
        self.assertEqual(result.status_code,503)
        self.assertIsNone(result.json()['value'])
        self.assertIsNone(result.json()['model_version'])
        self.assertEqual(result.json()['reason'],'model_unavailable')

    def test_service_schema_feature_and_body_limits(self):
        bad = fixture(); bad['feature_schema_version'] = 'unknown'
        self.assertEqual(self.client.post('/api/v1/predict',json=bad,headers=self.headers).status_code,422)
        bad = fixture(); bad['features'][0]['available_at'] = '2027-01-01T00:00:00Z'
        self.assertEqual(self.client.post('/api/v1/predict',json=bad,headers=self.headers).status_code,422)
        self.assertEqual(self.client.post('/api/v1/predict',content=b'x'*262145,headers=self.headers).status_code,413)

    def test_client_failures_are_unavailable_not_zero(self):
        for error, reason in ((requests.Timeout(),'service_timeout'),(requests.ConnectionError(),'service_unavailable')):
            client = MLClient('http://127.0.0.1:8001','synthetic-test-only',MagicMock(side_effect=error))
            result = client.predict(fixture())
            self.assertEqual(result['reason'],reason)
            self.assertIsNone(result['value'])
        self.assertEqual(MLClient().predict(fixture())['reason'],'service_not_configured')
        self.assertEqual(MLClient('http://external.invalid','synthetic-test-only').predict(fixture())['reason'],'service_configuration_invalid')

    def test_client_refuses_available_model_and_malformed_response(self):
        unavailable = evaluate_unavailable_request(fixture())
        bodies = [dict(unavailable,model_version='unapproved-model',value=0.5,status='available'),
                  dict(unavailable,value=0),dict(unavailable,data_quality='good'),[]]
        for body in bodies:
            response = MagicMock(status_code=503)
            response.json.return_value = body
            result = MLClient('http://localhost:8001','synthetic-test-only',MagicMock(return_value=response)).predict(fixture())
            self.assertEqual(result['reason'],'model_contract_mismatch')
            self.assertIsNone(result['value'])

    def test_client_contract_and_local_transport_headers(self):
        response = MagicMock(status_code=503)
        response.json.return_value = evaluate_unavailable_request(fixture())
        transport = MagicMock(return_value=response)
        result = MLClient('http://127.0.0.1:8001','synthetic-test-only',transport).predict(fixture())
        self.assertEqual(result['reason'],'model_unavailable')
        self.assertFalse(transport.call_args.kwargs['allow_redirects'])
        self.assertEqual(transport.call_args.kwargs['timeout'],(2,5))
        bad = deepcopy(fixture()); bad['feature_schema_version'] = 'unknown'
        with self.assertRaises(ValueError):
            MLClient().predict(bad)


if __name__ == '__main__':
    unittest.main()
