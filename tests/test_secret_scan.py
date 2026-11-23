"""Synthetic Git patches exercise history scanning without touching repository data."""
from secrets import token_hex
import unittest
from unittest.mock import patch

from scripts.scan_secrets import scan


def synthetic_diff(line):
    return ('diff --git a/synthetic.py b/synthetic.py\n'
            'new file mode 100644\n'
            '--- /dev/null\n'
            '+++ b/synthetic.py\n'
            '@@ -0,0 +1 @@\n+' + line + '\n').encode()


class HistoryScanTests(unittest.TestCase):
    def run_history(self, line):
        def fake_git(*args):
            if args[0] == 'ls-files':
                return b''
            if args[0] == 'rev-list':
                return b'synthetic-commit\n'
            if args[0] == 'show':
                return synthetic_diff(line)
            raise AssertionError('Unexpected Git operation')
        with patch('scripts.scan_secrets.git', side_effect=fake_git):
            return scan(staged=True, history=True)

    def test_root_commit_patch_without_secret(self):
        result = self.run_history('answer = 42')
        self.assertTrue(result['history_scanned'])
        self.assertEqual(result['findings'], [])

    def test_history_detects_generated_test_credential_without_exposing_value(self):
        # Random test bytes are never credentials for any service.
        value = token_hex(32)
        result = self.run_history('DB_PASSWORD = ' + repr(value))
        self.assertTrue(result['findings'])
        self.assertTrue(all(item['commit'] == 'synthetic-commit' for item in result['findings']))
        self.assertNotIn(value, repr(result))
