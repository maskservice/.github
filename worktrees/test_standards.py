import json
import unittest
from test_audit import AuditTests
import standards


class StandardsTests(AuditTests):
    def put(self, path, value):
        file = self.repo / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(value) if isinstance(value, dict) else value)
        self.git('add', path)

    def test_instruction_is_not_implementation(self):
        self.put('AGENTS.md', 'Use wellmanifest/worktrees v5.\n')
        result = standards.observe(self.repo)
        self.assertEqual(result['adoption'], 'instructions-only')
        self.assertEqual(result['pins'], [])

    def test_lifecycle_schedule_is_not_update_automation(self):
        self.put('.github/workflows/lifecycle.yml', 'on:\n  schedule:\n    - cron: "0 3 * * *"\n# wellmanifest lifecycle\n')
        self.assertEqual(standards.observe(self.repo)['scheduledFreshness'], [])

    def test_stale_adoption_projection_is_reported(self):
        self.put('.governance/manifest.lock.json', {'standard': {
            'id': 'wellmanifest/new-project', 'sourceRevision': 'a' * 40, 'version': '0.20.26'}, 'managedFiles': {}})
        self.put('.wellmanifest/adoption.json', {'standards': [{
            'id': 'wellmanifest/new-project', 'revision': 'b' * 40, 'version': '0.18.1', 'status': 'adopted'}]})
        self.assertIn('adoption-metadata-disagrees-with-lock',
                      [x['code'] for x in standards.observe(self.repo)['findings']])

    def test_declared_update_policy_without_hook_is_not_active(self):
        self.put('.governance/standard-adoption.json', {'updates': {'enabled': True}})
        self.assertFalse(standards.observe(self.repo)['precommitUpdateController'])

    def test_escaping_managed_artifact_is_drift(self):
        self.put('.governance/manifest.lock.json', {'standard': {
            'id': 'wellmanifest/new-project', 'sourceRevision': 'a' * 40, 'version': '0.20.26'},
            'managedFiles': {'../outside': '0' * 64}})
        self.assertEqual(standards.observe(self.repo)['findings'][0]['code'], 'managed-artifact-drift')


if __name__ == '__main__':
    unittest.main()
