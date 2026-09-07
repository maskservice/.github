import hashlib
import json
import os
from pathlib import Path
import unittest

from test_audit import AuditTests
import enforcement
import install_hook
import precommit


class EnforcementTests(AuditTests):
    def test_config_is_not_a_hook(self):
        self.git('config', 'core.hooksPath', '.githooks')
        self.assertIn('precommit-missing', [x['code'] for x in enforcement.observe(self.repo)['findings']])

    def test_direct_managed_ci_gate_is_recognized(self):
        workflow = self.repo / '.github/workflows/governance.yml'
        workflow.parent.mkdir(parents=True)
        workflow.write_text('jobs:\n  enforce:\n    steps:\n      - run: python3 .governance/governance_check.py --root .\n')
        record = enforcement.observe(self.repo)
        self.assertEqual(record['gateWorkflowCandidates'], ['.github/workflows/governance.yml'])
        self.assertNotIn('governance-ci-invocation-not-found', [x['code'] for x in record['findings']])

    def test_managed_drift_is_reported(self):
        target = self.repo / '.governance'
        target.mkdir()
        (target / 'manifest.lock.json').write_text(json.dumps({'managedFiles': {'AGENTS.md': hashlib.sha256(b'expected').hexdigest()}}))
        (self.repo / 'AGENTS.md').write_text('different')
        self.assertIn('managed-file-drift', [x['code'] for x in enforcement.observe(self.repo)['findings']])

    def test_runtime_data_staged_even_when_forced_is_blocked(self):
        path = self.repo / '.subactor/recovery/private.txt'
        path.parent.mkdir(parents=True)
        path.write_text('fixture')
        self.git('add', '-f', str(path))
        self.assertEqual(precommit.check(self.repo)[0]['code'], 'runtime-data-staged')
        install_hook.install(self.repo)
        result = __import__('subprocess').run(['git', '-C', str(self.repo), 'commit', '-qm', 'invalid'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('runtime-data-staged', result.stderr)

    def test_worktrees_standard_source_is_not_runtime_data(self):
        path = self.repo / 'worktrees/conformance.py'
        path.parent.mkdir()
        path.write_text('print("standard source")')
        self.git('add', str(path))
        self.assertEqual(precommit.check(self.repo), [])

    def test_runtime_manifest_is_allowed(self):
        path = self.repo / '.subactor/manifest.json'
        path.parent.mkdir()
        path.write_text(json.dumps({'managedFiles': {'.githooks/pre-commit': '0' * 64}}))
        self.git('add', str(path))
        self.assertEqual(precommit.check(self.repo), [])

    def test_noncanonical_writer_is_blocked_but_primary_is_not(self):
        path = self.repo.parent / 'legacy-writer'
        self.git('worktree', 'add', '--relative-paths', '-b', 'legacy', str(path))
        self.assertIn('noncanonical-registration', [x['code'] for x in precommit.check(path)])
        self.assertEqual(precommit.check(self.repo), [])

    def test_existing_hook_still_blocks_and_is_unchanged(self):
        old = self.repo / '.git/hooks/pre-commit'
        old.write_text('#!/bin/sh\necho original-policy >&2\nexit 17\n')
        old.chmod(0o755)
        before = old.read_bytes()
        install_hook.install(self.repo)
        install_hook.install(self.repo)
        result = __import__('subprocess').run(['git', '-C', str(self.repo), 'commit', '--allow-empty', '-m', 'fixture'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('original-policy', result.stderr)
        self.assertEqual(old.read_bytes(), before)

    def test_managed_hooks_path_is_preserved_for_the_official_validator(self):
        path = self.repo / '.governance/manifest.lock.json'
        path.parent.mkdir()
        path.write_text(json.dumps({'managedFiles': {'.githooks/pre-commit': '0' * 64}}))
        hook = self.repo / '.githooks/pre-commit'
        hook.parent.mkdir()
        hook.write_text('#!/bin/sh\nexit 0\n')
        hook.chmod(0o755)
        self.git('config', 'core.hooksPath', '.githooks')
        report = install_hook.install(self.repo)
        self.assertEqual(report['status'], 'managed-delegation')
        self.assertTrue(report['managedHookExecutable'])
        self.assertEqual(self.git('config', '--get', 'core.hooksPath').stdout.strip(), '.githooks')

    def test_later_managed_adoption_restores_its_original_hook_location(self):
        self.git('config', 'core.hooksPath', '.githooks')
        install_hook.install(self.repo)
        path = self.repo / '.governance/manifest.lock.json'
        path.parent.mkdir()
        path.write_text(json.dumps({'managedFiles': {'.githooks/pre-commit': '0' * 64}}))
        report = install_hook.install(self.repo)
        self.assertFalse(report['managedHookExecutable'])
        self.assertEqual(self.git('config', '--get', 'core.hooksPath').stdout.strip(), '.githooks')
        self.assertIn('managed-precommit-missing', [x['code'] for x in enforcement.observe(self.repo)['findings']])

    def test_legacy_package_gets_guard_without_claiming_full_adoption(self):
        lock = self.repo / '.governance/manifest.lock.json'
        lock.parent.mkdir()
        lock.write_text(json.dumps({'managedFiles': {}}))
        report = install_hook.install(self.repo)
        self.assertIn('offlineGuard', report)
        result = __import__('subprocess').run(['git', '-C', str(self.repo), 'commit', '--allow-empty', '-m', 'legacy'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = enforcement.observe(self.repo)
        self.assertTrue(record['precommitExecutable'])
        self.assertIn('managed-host-contract-not-adopted', [x['code'] for x in record['findings']])
        path = self.repo / '.subactor/cache/private'
        path.parent.mkdir(parents=True)
        path.write_text('private')
        self.git('add', '-f', str(path))
        result = __import__('subprocess').run(['git', '-C', str(self.repo), 'commit', '-m', 'invalid'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('runtime-data-staged', result.stderr)

    def test_legacy_previous_delegation_can_receive_guard(self):
        self.git('config', 'core.hooksPath', '.githooks')
        install_hook.install(self.repo)
        state_path = self.repo / '.git/maskservice-hook-state.json'
        state = json.loads(state_path.read_text())
        state['mode'] = 'managed-delegation'
        state_path.write_text(json.dumps(state))
        self.git('config', 'core.hooksPath', '.githooks')
        lock = self.repo / '.governance/manifest.lock.json'
        lock.parent.mkdir()
        lock.write_text(json.dumps({'managedFiles': {}}))
        self.assertIn('offlineGuard', install_hook.install(self.repo))

    def test_staged_ignore_regression_cannot_hide_behind_working_copy(self):
        ignore = self.repo / '.gitignore'
        original = ignore.read_text()
        ignore.write_text(original.replace('/.subactor/cache/\n', ''))
        self.git('add', '.gitignore')
        ignore.write_text(original)
        self.assertIn('ignore-policy-regressed', [x['code'] for x in precommit.check(self.repo)])

    def test_deleting_adopted_ignore_policy_is_blocked(self):
        self.git('rm', '.gitignore')
        findings = precommit.check(self.repo)
        self.assertEqual(len([x for x in findings if x['code'] == 'ignore-policy-regressed']), 7)

    def test_foreign_hooks_change_is_preserved(self):
        install_hook.install(self.repo)
        self.git('config', 'core.hooksPath', '/another-owner')
        with self.assertRaises(ValueError):
            install_hook.install(self.repo)
        self.assertEqual(self.git('config', '--get', 'core.hooksPath').stdout.strip(), '/another-owner')


if __name__ == '__main__':
    unittest.main()
