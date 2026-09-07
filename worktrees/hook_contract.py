"""Recognize hook ownership from package evidence, including missing files."""
import json
from pathlib import Path

CONTRACTS = ('governance/agent-hosts.json', '.governance/agent-hosts.json')


def owns_hook(repo):
    repo = Path(repo)
    lock = repo / '.governance/manifest.lock.json'
    if lock.is_file():
        managed = json.loads(lock.read_text()).get('managedFiles', {})
        # A deleted contract/hook still belongs to its pinned package.
        if '.githooks/pre-commit' in managed or any(p in managed for p in CONTRACTS):
            return True
    return any((repo / p).is_file() for p in CONTRACTS)
