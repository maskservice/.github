import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('audit', Path(__file__).with_name('audit.py'))
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    def setUp(self):
        # Test fixtures stay in ignored repository-local storage.
        cache = Path(__file__).resolve().parents[1] / '.subactor/cache'
        cache.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=cache)
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'example'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.name', 'Audit Test')
        self.git('config', 'user.email', 'audit@example.invalid')
        (self.repo / '.gitignore').write_text('\n'.join(audit.IGNORES) + '\n')
        self.git('add', '.gitignore')
        self.git('commit', '-qm', 'fixture')

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args],
                              capture_output=True, text=True, check=True)

    def test_primary_without_worktrees_passes(self):
        self.assertEqual(audit.audit(self.repo)['findings'], [])

    def test_canonical_relative_worktree_requires_lease(self):
        path = self.repo / '.worktrees/ticket-001--test'
        self.git('worktree', 'add', '--relative-paths', '-b', 'ticket/001-test', str(path))
        report = audit.audit(self.repo)
        self.assertEqual([f['code'] for f in report['findings']], ['missing-lease'])
        self.assertEqual(list(audit.repositories(self.repo)), [self.repo])

    def test_external_worktree_is_reported_without_changes(self):
        path = self.repo.parent / 'legacy'
        self.git('worktree', 'add', '--relative-paths', '-b', 'legacy', str(path))
        before = self.git('worktree', 'list', '--porcelain').stdout
        self.assertIn('noncanonical-registration', [f['code'] for f in audit.audit(self.repo)['findings']])
        self.assertEqual(before, self.git('worktree', 'list', '--porcelain').stdout)
        self.assertTrue((path / '.git').is_file())

    def test_absolute_links_are_reported(self):
        path = self.repo / '.worktrees/ticket-001--test'
        self.git('worktree', 'add', '--no-relative-paths', '-b', 'ticket/001-test', str(path))
        codes = [f['code'] for f in audit.audit(self.repo)['findings']]
        self.assertIn('absolute-git-pointer', codes)
        self.assertIn('missing-or-absolute-back-pointer', codes)

    def test_branch_must_match_layout(self):
        path = self.repo / '.worktrees/ticket-001--test'
        self.git('worktree', 'add', '--relative-paths', '-b', 'unrelated', str(path))
        self.assertIn('branch-layout-mismatch', [f['code'] for f in audit.audit(self.repo)['findings']])

    def test_broad_ignore_cannot_hide_manifest(self):
        with (self.repo / '.gitignore').open('a') as handle:
            handle.write('/.subactor/\n')
        self.assertIn('subactor-manifest-ignored', [f['code'] for f in audit.audit(self.repo)['findings']])


if __name__ == '__main__':
    unittest.main()
