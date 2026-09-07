#!/usr/bin/env python3
"""Read-only local audit; GitHub CI cannot observe developers' worktree registries."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
IGNORES = ['/.worktrees/'] + [f'/.subactor/{part}/' for part in
    ('leases', 'sessions', 'recovery', 'receipts', 'cache', 'snapshots')]
SKIP = {'.git', '.worktrees', 'worktrees', 'node_modules', '.venv', 'venv',
        '__pycache__', '.cache', 'dist', 'build', 'storage'}


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True).stdout


def repositories(root):
    for base, dirs, files in os.walk(root):
        if '.git' in dirs or '.git' in files:
            yield Path(base)
        dirs[:] = [d for d in dirs if d not in SKIP and not (Path(base) / d).is_symlink()]


def checker(*args, cwd):
    return json.loads(run(sys.executable, str(HERE / 'vendor/conformance.py'), *args, cwd=cwd))


def audit(repo):
    record = checker('inventory', '--repository', repo.name, '--repository-name', repo.name,
                     '--from-worktree', str(repo), cwd=repo)
    primary = Path(record['primaryCheckout'])
    findings = []
    ignore = primary / '.gitignore'
    lines = ignore.read_text().splitlines() if ignore.exists() else []
    for rule in IGNORES:
        if rule not in lines:
            findings.append({'code': 'missing-root-ignore', 'rule': rule})
    for entry in record['entries'][1:]:
        path = Path(entry['path'])
        if entry['classification'] != 'canonical-v5':
            findings.append({'code': 'noncanonical-registration', 'path': str(path),
                             'classification': entry['classification']})
        else:
            lease = primary / '.subactor/leases' / (path.name + '.json')
            # Existence is only an observation; this tool does not authenticate ownership.
            entry['leaseExists'] = lease.is_file()
            if not lease.is_file():
                findings.append({'code': 'missing-lease', 'path': str(path)})
        for anomaly in entry['anomalies']:
            findings.append({'code': anomaly, 'path': str(path)})
        pointer = path / '.git'
        if not pointer.is_file():
            findings.append({'code': 'missing-git-pointer', 'path': str(path)})
            continue
        value = pointer.read_text().strip()
        if not value.startswith('gitdir: '):
            findings.append({'code': 'invalid-git-pointer', 'path': str(path)})
            continue
        admin = value.removeprefix('gitdir: ')
        if os.path.isabs(admin):
            findings.append({'code': 'absolute-git-pointer', 'path': str(path)})
        back = (path / admin) / 'gitdir'
        if not back.is_file() or os.path.isabs(back.read_text().strip()):
            findings.append({'code': 'missing-or-absolute-back-pointer', 'path': str(path)})
    record['findings'] = findings
    record['leaseValidation'] = 'existence-only; ownership, binding and expiry require runtime validation'
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    source = json.loads((HERE / 'vendor/source.json').read_text())
    for name, artifact in source['artifacts'].items():
        if hashlib.sha256((HERE / 'vendor' / name).read_bytes()).hexdigest() != artifact['sha256']:
            parser.error(f'Pinned checker artifact changed: {name}')
    records, seen, errors = [], set(), []
    for repo in repositories(args.root.resolve()):
        try:
            record = audit(repo)
            if record['primaryCheckout'] not in seen:
                records.append(record)
                seen.add(record['primaryCheckout'])
        except (subprocess.CalledProcessError, OSError, ValueError) as exc:
            errors.append({'repository': str(repo), 'error': str(exc)})
    result = {'standard': source, 'readOnly': True, 'repositories': records, 'errors': errors}
    if not records:
        errors.append({'error': 'No repositories found'})
    print(json.dumps(result, indent=2))
    return int(bool(errors) or any(r['findings'] for r in records))


if __name__ == '__main__':
    raise SystemExit(main())
