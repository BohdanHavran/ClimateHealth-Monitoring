"""Offline security regressions; no DB, AWS or medical observations."""
import os
import ssl
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

import pymysql
import requests
from climate_health.tls import mysql_tls_options, DatabaseTLSConfigurationError
from climate_health.ml_client import MLClient
from test_ml_http import fixture

ROOT = Path(__file__).resolve().parents[1]


class DeploymentReadinessTests(unittest.TestCase):
    def test_local_mysql_explicitly_disables_tls_without_changing_server(self):
        self.assertEqual(mysql_tls_options('localhost', {}), {'ssl_disabled': True})

    def test_aws_and_rds_hostname_enforce_identity(self):
        for host, env in [('db.internal', {'CLIMATE_ENV': 'aws'}), ('db.rds.amazonaws.com', {})]:
            ctx = mysql_tls_options(host, env)['ssl']
            self.assertTrue(ctx.check_hostname)
            self.assertEqual(ctx.verify_mode, ssl.CERT_REQUIRED)
            self.assertGreaterEqual(ctx.minimum_version, ssl.TLSVersion.TLSv1_2)
            self.assertGreater(ctx.cert_store_stats()['x509_ca'], 0)

    def test_aws_cannot_downgrade_or_use_missing_ca(self):
        for env in [{'DB_TLS_MODE': 'disabled'}, {'DB_TLS_MODE': 'required'}, {'DB_TLS_CA_FILE': 'missing-test-ca.crt'}]:
            with self.assertRaises(DatabaseTLSConfigurationError):
                mysql_tls_options('db.internal', dict(env, CLIMATE_ENV='aws'))

    def test_pymysql_rejects_plaintext_server_before_sending_authentication(self):
        connection = pymysql.Connection(host='db.internal', user='synthetic-user', defer_connect=True,
                                       **mysql_tls_options('db.internal', {'CLIMATE_ENV': 'aws'}))
        connection.server_version = '8.4.0'
        connection.server_capabilities = 0
        with patch.object(connection, 'write_packet') as write:
            with self.assertRaises(pymysql.err.OperationalError) as error:
                connection._request_authentication()
            self.assertEqual(error.exception.args[0], 2026)
            write.assert_not_called()

    def test_mysql_readiness_sanitizes_tls_failure(self):
        import climat
        with patch('climat.get_db', side_effect=DatabaseTLSConfigurationError('synthetic sensitive path')):
            response = climat.app.test_client().get('/health/ready')
        self.assertEqual(response.status_code, 503)
        self.assertNotIn('sensitive', response.get_data(as_text=True))

    def test_mysql_wrapped_hostname_failure_is_classified(self):
        import climat
        from climate_health.tls import DatabaseTLSVerificationError
        error = pymysql.err.OperationalError(2003, 'synthetic connection error')
        error.original_exception = ssl.SSLCertVerificationError('synthetic hostname mismatch')
        with climat.app.app_context(), patch('climat.get_db_password', return_value='synthetic-test-only'), patch('climat.pymysql.connect', side_effect=error):
            with self.assertRaises(DatabaseTLSVerificationError):
                climat.get_db()

    def test_ml_https_identity_and_timeouts_are_explicit(self):
        transport = MagicMock(side_effect=requests.Timeout())
        with patch.dict(os.environ, {'CLIMATE_ENV': 'aws', 'ML_CONNECT_TIMEOUT': '2', 'ML_READ_TIMEOUT': '5'}):
            result = MLClient('https://ml.internal:8001', 'synthetic-test-only', transport,
                              allowed_host='ml.internal').predict(fixture())
        self.assertEqual(result['reason'], 'service_timeout')
        self.assertTrue(transport.call_args.kwargs['verify'])
        self.assertFalse(transport.call_args.kwargs['allow_redirects'])
        self.assertEqual(transport.call_args.kwargs['timeout'], (2, 5))

    def test_ml_tls_failure_is_not_prediction(self):
        client = MLClient('https://ml.internal:8001', 'synthetic-test-only',
                          MagicMock(side_effect=requests.exceptions.SSLError()), allowed_host='ml.internal')
        result = client.predict(fixture())
        self.assertEqual(result['reason'], 'service_tls_failed')
        self.assertIsNone(result['value'])

    def test_ml_rejects_unsafe_endpoint_without_network(self):
        for url in ['http://localhost:8001', 'https://wrong.internal', 'https://ml.internal/a',
                    'https://user@ml.internal', 'https://ml.internal\n', 'https://ml.internal:99999']:
            transport = MagicMock()
            with patch.dict(os.environ, {'CLIMATE_ENV': 'aws'}):
                result = MLClient(url, 'synthetic-test-only', transport, allowed_host='ml.internal').predict(fixture())
            self.assertEqual(result['reason'], 'service_configuration_invalid')
            transport.assert_not_called()

    def test_ml_rejects_unbounded_timeouts(self):
        for timeout in ['nan', 'inf', '0', '31', 'bad']:
            transport = MagicMock()
            with patch.dict(os.environ, {'ML_READ_TIMEOUT': timeout}):
                result = MLClient('http://localhost:8001', 'synthetic-test-only', transport).predict(fixture())
            self.assertEqual(result['reason'], 'service_configuration_invalid')
            transport.assert_not_called()

    def test_stateful_protection_is_independent_of_application_count(self):
        base = ROOT / 'infrastructure/terraform/modules'
        for name in ['frontend', 'ecr', 'mysql']:
            self.assertIn('prevent_destroy = true', (base/name/'main.tf').read_text())
        from scripts.audit_terraform import blocks
        root = ROOT/'infrastructure/terraform'
        parsed = blocks(root/'main.tf', root)
        log = next(b for b in parsed if b['kind']=='resource' and b['labels']==['aws_cloudwatch_log_group','backend'])
        self.assertNotIn('count', log['attrs'])
        self.assertIn('prevent_destroy = true', log['body'])
        for module in ['database', 'frontend', 'ecr']:
            call = next(b for b in parsed if b['kind']=='module' and b['labels']==[module])
            self.assertNotIn('count', call['attrs'])
        self.assertFalse((base/'ai').exists())
        self.assertTrue(all('moved {' not in p.read_text() for p in root.rglob('*.tf')))

    def test_no_broad_alb_barrier_and_tls_copied_to_image(self):
        main = (ROOT/'infrastructure/terraform/main.tf').read_text()
        backend = (ROOT/'infrastructure/terraform/modules/ecs-backend/main.tf').read_text()
        self.assertNotIn('depends_on = [module.alb]', main)
        self.assertIn('condition = var.listener_rule_arn != null', backend)
        self.assertIn('DB_TLS_MODE",value="verify_identity"', backend)
        self.assertIn('infrastructure/certificates/ ./infrastructure/certificates/', (ROOT/'Dockerfile').read_text())
        import ssl

        region = 'eu-north-1'
        bundle = f'infrastructure/certificates/rds-{region}-bundle.crt'
        self.assertIn('rds-${var.region}-bundle.crt', backend)
        self.assertIn(f'!{bundle}', (ROOT/'.dockerignore').read_text().splitlines())
        context = ssl.create_default_context(cafile=str(ROOT / bundle))
        self.assertTrue(context.get_ca_certs())
        self.assertTrue(context.check_hostname)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
