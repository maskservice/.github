import subprocess
from test_audit import AuditTests
import install_hook
import prepush
import repository_policy


class PushTests(AuditTests):
    def tip(self):
        return self.git('rev-parse', 'HEAD').stdout.strip()

    def test_committed_ignore_regression_cannot_hide_in_working_copy(self):
        ignore = self.repo / '.gitignore'
        original = ignore.read_text()
        ignore.write_text(original.replace('/.subactor/cache/\n', ''))
        self.git('commit', '-am', 'remove protection')
        ignore.write_text(original)
        self.assertIn('committed-ignore-rule-missing', [r['code'] for r in repository_policy.check(self.repo)])

    def test_private_intermediate_commit_is_rejected_after_tip_removes_it(self):
        base = self.tip()
        private = self.repo / '.subactor/cache/private'
        private.parent.mkdir(parents=True)
        private.write_text('fixture')
        self.git('add', '-f', str(private))
        self.git('commit', '-m', 'private')
        self.git('rm', str(private))
        self.git('commit', '-m', 'remove private')
        self.assertEqual(repository_policy.check(self.repo), [])
        findings = prepush.inspect(self.repo, 'origin', f'refs/heads/main {self.tip()} refs/heads/main {base}\n')
        self.assertIn('outgoing-runtime-data', [r['code'] for r in findings])

    def test_real_push_is_blocked_even_when_commit_skipped_hooks(self):
        remote = self.repo.parent / 'remote.git'
        subprocess.run(['git', 'init', '--bare', '-q', str(remote)], check=True)
        self.git('remote', 'add', 'origin', str(remote))
        self.git('push', 'origin', 'HEAD:refs/heads/main')
        install_hook.install(self.repo)
        path = self.repo / '.subactor/cache/private'
        path.parent.mkdir(parents=True)
        path.write_text('fixture')
        self.git('add', '-f', str(path))
        self.git('-c', 'core.hooksPath=/dev/null', 'commit', '-m', 'skipped commit hook')
        result = subprocess.run(['git', '-C', str(self.repo), 'push', 'origin', 'HEAD:refs/heads/main'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('MASKSERVICE-PREPUSH', result.stderr)

    def test_original_prepush_receives_arguments_and_complete_stdin(self):
        original = self.repo / '.git/hooks/pre-push'
        original.write_text('#!/bin/sh\ncat > hook-input\nprintf "%s" "$1" > hook-remote\nexit 19\n')
        original.chmod(0o755)
        installed = install_hook.install(self.repo)
        payload = f'refs/heads/main {self.tip()} refs/heads/main {self.tip()}\n'
        result = subprocess.run([installed['hooksPath'] + '/pre-push', 'origin', 'fixture'], cwd=self.repo, input=payload, text=True, capture_output=True)
        self.assertEqual(result.returncode, 19, result.stderr)
        self.assertEqual((self.repo / 'hook-input').read_text(), payload)
        self.assertEqual((self.repo / 'hook-remote').read_text(), 'origin')

    def test_malformed_reference_cannot_pass(self):
        with self.assertRaises(ValueError):
            prepush.inspect(self.repo, 'origin', 'invalid record')

    def test_deleting_reference_does_not_require_missing_object(self):
        self.assertEqual(prepush.inspect(self.repo, 'origin', f'(delete) {"0" * 40} refs/heads/old {self.tip()}'), [])
