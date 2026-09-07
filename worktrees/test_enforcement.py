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
        path.write_text('{}')
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

    def test_missing_declared_managed_hook_fails_closed(self):
        path = self.repo / '.governance/manifest.lock.json'
        path.parent.mkdir()
        path.write_text('{}')
        self.git('config', 'core.hooksPath', '.githooks')
        install_hook.install(self.repo)
        result = __import__('subprocess').run(['git', '-C', str(self.repo), 'commit', '--allow-empty', '-m', 'fixture'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('declared managed pre-commit', result.stderr)

    def test_foreign_hooks_change_is_preserved(self):
        install_hook.install(self.repo)
        self.git('config', 'core.hooksPath', '/another-owner')
        with self.assertRaises(ValueError):
            install_hook.install(self.repo)
        self.assertEqual(self.git('config', '--get', 'core.hooksPath').stdout.strip(), '/another-owner')


if __name__ == '__main__':
    unittest.main()
