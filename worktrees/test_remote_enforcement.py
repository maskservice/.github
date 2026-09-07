import unittest
from unittest.mock import patch
from types import SimpleNamespace
import remote_enforcement as remote


class RemoteTests(unittest.TestCase):
    def test_green_checks_are_not_inferred_from_missing_protection(self):
        result = remote.summarize([], None)
        self.assertEqual(len(result['findings']), 3)
        self.assertEqual(result['checkRunResults'], 'not-observed')

    def test_history_protection_does_not_claim_required_ci(self):
        result = remote.summarize(remote.POLICY['rules'], None)
        self.assertEqual(result['findings'], ['required-status-checks-missing'])

    def test_classic_and_ruleset_checks_are_combined(self):
        rules = remote.POLICY['rules'] + [{'type': 'required_status_checks', 'parameters': {'required_status_checks': [{'context': 'governance'}]}}]
        result = remote.summarize(rules, {'required_status_checks': {'contexts': ['tests']}})
        self.assertEqual(result['requiredCheckContexts'], ['governance', 'tests'])
        self.assertEqual(result['findings'], [])

    def test_permission_error_is_not_reported_as_no_protection(self):
        with patch('remote_enforcement.subprocess.run', return_value=SimpleNamespace(returncode=1, stdout='{"status":"404","message":"Not Found"}')):
            with self.assertRaises(remote.ApiError):
                remote.api('repos/example/private')

    def test_explicit_unprotected_response_is_understood(self):
        with patch('remote_enforcement.subprocess.run', return_value=SimpleNamespace(returncode=1, stdout='{"status":"404","message":"Branch not protected"}')):
            self.assertIsNone(remote.api('repos/example/public/branches/main/protection'))

    def test_mutation_preserves_other_rulesets_and_has_no_bypass(self):
        calls = []
        def request(path, method='GET', body=None):
            calls.append((path, method, body))
            if path.endswith('?per_page=100'):
                return [{'name': 'existing-governance', 'id': 1}]
            if method == 'POST':
                self.assertEqual(body['bypass_actors'], [])
                self.assertEqual(body['conditions']['ref_name']['include'], ['~DEFAULT_BRANCH'])
                return {'id': 2}
            return {'permissions': {'admin': True}}
        self.assertEqual(remote.protect_history('maskservice/example', request)['action'], 'created')
        self.assertEqual([c[1] for c in calls], ['GET', 'GET', 'POST'])

    def test_external_repositories_are_read_only(self):
        with self.assertRaises(ValueError):
            remote.protect_history('wellmanifest/new-project', lambda *_: self.fail('API called'))

    def test_existing_changed_policy_is_not_overwritten(self):
        def request(path, *args):
            if path.endswith('?per_page=100'):
                return [{'name': remote.NAME, 'source': 'maskservice/example', 'id': 3}]
            if path.endswith('/3'):
                return {**remote.POLICY, 'id': 3, 'enforcement': 'disabled'}
            return {'permissions': {'admin': True}}
        with self.assertRaises(ValueError):
            remote.protect_history('maskservice/example', request)

    def test_matching_policy_is_idempotent(self):
        def request(path, method='GET', body=None):
            self.assertEqual(method, 'GET')
            if path.endswith('?per_page=100'):
                return [{'name': remote.NAME, 'source': 'maskservice/example', 'id': 3}]
            if path.endswith('/3'):
                return {**remote.POLICY, 'id': 3}
            return {'permissions': {'admin': True}}
        self.assertEqual(remote.protect_history('maskservice/example', request), {'action': 'unchanged', 'id': 3})

    def test_empty_required_check_rule_does_not_satisfy_ci(self):
        rules = remote.POLICY['rules'] + [{'type': 'required_status_checks', 'parameters': {'required_status_checks': []}}]
        self.assertIn('required-status-checks-missing', remote.summarize(rules, None)['findings'])
