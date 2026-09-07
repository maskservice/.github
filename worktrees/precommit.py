#!/usr/bin/env python3
"""Local placement guard. Complements, never replaces, the repository's tests."""
import json
from pathlib import Path
import subprocess
import sys

import audit

OPERATIONAL = {'.worktrees'}
RUNTIME_PARTS = {'leases', 'sessions', 'recovery', 'receipts', 'cache', 'snapshots'}


def staged_findings(repo):
    raw = subprocess.check_output(['git', '-C', str(repo), 'diff', '--cached', '--name-only',
                                   '--diff-filter=ACMR', '-z'])
    issues = []
    for name in raw.decode('utf-8', errors='surrogateescape').split('\0'):
        parts = Path(name).parts
        if not parts:
            continue
        if parts[0] in OPERATIONAL or (len(parts) > 1 and parts[0] == '.subactor' and parts[1] in RUNTIME_PARTS):
            issues.append({'code': 'runtime-data-staged', 'path': name})
    return issues


def check(repo):
    repo = Path(repo).resolve()
    record = audit.audit(repo)
    issues = staged_findings(repo)
    # Historical peers remain recovery inventory. A primary commit must not
    # be blocked merely because a different historical checkout exists.
    if repo != Path(record['primaryCheckout']).resolve():
        issues.extend(f for f in record['findings'] if f.get('path') == str(repo))
    return issues


def main():
    try:
        root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()
        # Verify the packaged upstream checker before using it, including when
        # this file was installed as an offline hook snapshot.
        audit.verify_source()
        issues = check(root)
        if issues:
            print('MASKSERVICE-PRECOMMIT: placement/data policy failed', file=sys.stderr)
            print(json.dumps(issues, indent=2), file=sys.stderr)
        return int(bool(issues))
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f'MASKSERVICE-PRECOMMIT: cannot verify policy: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
