"""Reject committed policy regressions and private data in outgoing history."""
import json
from pathlib import Path
import re
import subprocess
import sys

from repository_policy import check, git, private_path


def inspect(root, remote, lines):
    findings = []
    seen = set()
    for line in lines.splitlines():
        parts = line.split()
        if len(parts) != 4:
            raise ValueError('Invalid pre-push reference record')
        _, local, _, previous = parts
        if not all(re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', oid) for oid in (local, previous)):
            raise ValueError('Invalid pre-push object identity')
        if not local.strip('0'):
            continue
        findings.extend(check(root, local))
        args = ['rev-list', local]
        if previous.strip('0'):
            args.append('^' + previous)
        else:
            args += ['--not', '--remotes=' + remote]
        for commit in git(root, *args).decode().splitlines():
            if commit in seen:
                continue
            seen.add(commit)
            paths = git(root, 'diff-tree', '--root', '-m', '--no-commit-id', '--name-only',
                        '--diff-filter=ACMR', '-r', '-z', commit).decode('utf-8', 'surrogateescape').split('\0')
            findings.extend({'code': 'outgoing-runtime-data', 'commit': commit, 'path': path}
                            for path in filter(None, paths) if private_path(path))
    return findings


def main():
    try:
        root = Path(git('.', 'rev-parse', '--show-toplevel').decode().strip())
        findings = inspect(root, sys.argv[1], sys.stdin.read())
        if findings:
            print('MASKSERVICE-PREPUSH: ' + json.dumps(findings), file=sys.stderr)
        return int(bool(findings))
    except (IndexError, ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f'MASKSERVICE-PREPUSH: cannot verify outgoing data: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
