"""Check committed repository data policy without importing repository code."""
import argparse
import json
from pathlib import Path
import subprocess

PARTS = ('leases', 'sessions', 'recovery', 'receipts', 'cache', 'snapshots')
RULES = ['/.worktrees/'] + [f'/.subactor/{part}/' for part in PARTS]


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def private_path(name):
    parts = Path(name).parts
    return bool(parts and (parts[0] == '.worktrees' or
                           (len(parts) > 1 and parts[0] == '.subactor' and parts[1] in PARTS)))


def check(root, revision='HEAD'):
    oid = git(root, 'rev-parse', '--verify', f'{revision}^{{commit}}').decode().strip()
    entries = git(root, 'ls-tree', '-r', '-z', oid).decode('utf-8', 'surrogateescape').split('\0')
    files = {}
    findings = []
    for entry in filter(None, entries):
        metadata, path = entry.split('\t', 1)
        files[path] = metadata.split()
        if private_path(path):
            findings.append({'code': 'committed-runtime-data', 'path': path})
    if '.gitignore' not in files or files['.gitignore'][0] not in ('100644', '100755'):
        findings.append({'code': 'committed-ignore-policy-missing'})
    else:
        rules = git(root, 'show', f'{oid}:.gitignore').decode().splitlines()
        findings.extend({'code': 'committed-ignore-rule-missing', 'rule': rule}
                        for rule in RULES if rule not in rules)
        # Broad root ignores hide the trackable runtime manifest. Exact private
        # namespaces are required by Worktrees v5; do not accept a blanket rule.
        if any(rule.strip() in ('.subactor', '.subactor/', '/.subactor', '/.subactor/') for rule in rules):
            findings.append({'code': 'blanket-runtime-ignore'})
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository', type=Path)
    parser.add_argument('--revision', default='HEAD')
    args = parser.parse_args()
    try:
        findings = check(args.repository, args.revision)
        print(json.dumps({'revision': args.revision, 'findings': findings}))
        return int(bool(findings))
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({'error': str(exc)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
