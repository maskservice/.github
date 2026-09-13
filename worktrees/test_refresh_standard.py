import hashlib
import json
from unittest.mock import patch
from test_audit import AuditTests
import refresh_standard


class RefreshTests(AuditTests):
    def setUp(self):
        super().setUp()
        self.vendor = self.repo / 'worktrees/vendor'
        self.vendor.mkdir(parents=True)
        artifacts = {}
        for name, source in [('conformance.py', 'operations/conformance.py'),
                             ('worktrees.schema.json', 'models/worktrees.schema.json')]:
            (self.vendor / name).write_bytes(b'old')
            artifacts[name] = {'sourcePath': source, 'sha256': hashlib.sha256(b'old').hexdigest()}
        (self.vendor / 'source.json').write_text(json.dumps({
            'repository': 'wellmanifest/worktrees', 'revision': 'a' * 40,
            'version': '0.5.1', 'artifacts': artifacts}))

    def test_local_drift_refuses_before_network_or_write(self):
        (self.vendor / 'conformance.py').write_bytes(b'user changes')
        with patch.object(refresh_standard, 'api') as fetch:
            with self.assertRaises(ValueError):
                refresh_standard.plan(self.repo, '0.5.3', 'b' * 40)
            fetch.assert_not_called()

    def test_download_failure_preserves_every_original(self):
        before = {p.name: p.read_bytes() for p in self.vendor.iterdir()}
        with patch.object(refresh_standard, 'api', side_effect=[b'new', OSError('offline')]):
            with self.assertRaises(OSError):
                refresh_standard.plan(self.repo, '0.5.3', 'b' * 40)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.vendor.iterdir()})

    def test_plan_binds_downloaded_bytes_without_writing(self):
        with patch.object(refresh_standard, 'api', return_value=b'new'):
            changes = refresh_standard.plan(self.repo, '0.5.3', 'b' * 40)
        lock = json.loads(changes[self.vendor / 'source.json'])
        self.assertEqual(lock['revision'], 'b' * 40)
        self.assertEqual(lock['artifacts']['conformance.py']['sha256'], hashlib.sha256(b'new').hexdigest())
        self.assertEqual((self.vendor / 'conformance.py').read_bytes(), b'old')

    def test_lightweight_tag_is_rejected(self):
        release = {'tag_name': 'v0.5.3', 'draft': False, 'prerelease': False, 'published_at': 'today'}
        with patch.object(refresh_standard, 'api', side_effect=[release, {'object': {'type': 'commit'}}]):
            with self.assertRaises(ValueError):
                refresh_standard.published()
