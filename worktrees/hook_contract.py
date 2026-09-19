import json
from pathlib import Path
import subprocess

CONTRACTS = ('governance/agent-hosts.json', '.governance/agent-hosts.json')


def _check_managed_files(managed):
    if not isinstance(managed, dict):
        return False
    return '.githooks/pre-commit' in managed or any(p in managed for p in CONTRACTS)


def _check_lock_content(text):
    try:
        data = json.loads(text)
        return _check_managed_files(data.get('managedFiles', {}))
    except (ValueError, TypeError, json.JSONDecodeError):
        return False


def _check_dir(path):
    p = Path(path)
    lock = p / '.governance/manifest.lock.json'
    if lock.is_file():
        try:
            if _check_lock_content(lock.read_text()):
                return True
        except OSError:
            pass
    return any((p / c).is_file() for c in CONTRACTS)


def _check_git(repo):
    try:
        candidate_refs = ['origin/main', 'origin/master', 'origin/HEAD']
        res = subprocess.run(['git', '-C', str(repo), 'rev-parse', '--abbrev-ref', '@{upstream}'],
                             capture_output=True, text=True)
        if res.returncode == 0:
            upstream = res.stdout.strip()
            if upstream and upstream not in candidate_refs:
                candidate_refs.insert(0, upstream)

        for ref in candidate_refs:
            show_res = subprocess.run(['git', '-C', str(repo), 'show', f'{ref}:.governance/manifest.lock.json'],
                                      capture_output=True, text=True)
            if show_res.returncode == 0 and _check_lock_content(show_res.stdout):
                return True
            for c in CONTRACTS:
                cat_res = subprocess.run(['git', '-C', str(repo), 'cat-file', '-e', f'{ref}:{c}'],
                                         capture_output=True)
                if cat_res.returncode == 0:
                    return True

        wt_res = subprocess.run(['git', '-C', str(repo), 'worktree', 'list', '--porcelain'],
                                capture_output=True, text=True)
        if wt_res.returncode == 0:
            for line in wt_res.stdout.splitlines():
                if line.startswith('worktree '):
                    wt_dir = Path(line.removeprefix('worktree ').strip())
                    if wt_dir.resolve() != repo.resolve() and _check_dir(wt_dir):
                        return True

        wt_root = repo / '.worktrees'
        if wt_root.is_dir():
            for child in wt_root.iterdir():
                if child.is_dir() and child.resolve() != repo.resolve() and _check_dir(child):
                    return True
    except (subprocess.SubprocessError, OSError, ValueError):
        pass
    return False


def owns_hook(repo):
    repo = Path(repo)
    if _check_dir(repo):
        return True
    return _check_git(repo)

