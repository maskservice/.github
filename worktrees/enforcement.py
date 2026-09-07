#!/usr/bin/env python3
"""Observe host enforcement separately from policy files; never run arbitrary hooks."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

import audit


def git(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True)
    if result.returncode:
        raise ValueError(f'git {args[0]} failed ({result.returncode})')
    return result.stdout.strip()


def observe(repo):
    repo = Path(repo).resolve()
    hook = Path(git(repo, 'rev-parse', '--path-format=absolute', '--git-path', 'hooks/pre-commit'))
    findings = []
    if not hook.is_file():
        findings.append({'code': 'precommit-missing'})
    elif not os.access(hook, os.X_OK):
        findings.append({'code': 'precommit-not-executable'})
    state_path = Path(git(repo, 'rev-parse', '--path-format=absolute', '--git-common-dir')) / 'maskservice-hook-state.json'
    original_hook = hook
    if state_path.is_file():
        state = json.loads(state_path.read_text())
        original = Path(state['previousHooksPath'] or state['previousDefaultDirectory'])
        original_hook = (original if original.is_absolute() else repo / original) / 'pre-commit'
        expected = state_path.parent / 'maskservice-hooks/pre-commit'
        if state.get('mode') != 'managed-delegation' and hook != expected:
            findings.append({'code': 'installed-placement-guard-not-active'})
    lock_path = repo / '.governance/manifest.lock.json'
    lock = json.loads(lock_path.read_text()) if lock_path.is_file() else None
    if lock is None:
        findings.append({'code': 'managed-standard-pin-missing'})
    else:
        if not original_hook.is_file() or not os.access(original_hook, os.X_OK):
            findings.append({'code': 'managed-precommit-missing'})
        for relative, digest in lock.get('managedFiles', {}).items():
            path = repo / relative
            if not path.resolve().is_relative_to(repo):
                findings.append({'code': 'managed-path-outside-repository', 'path': relative})
                continue
            if not path.is_file():
                findings.append({'code': 'managed-file-missing', 'path': relative})
            elif hashlib.sha256(path.read_bytes()).hexdigest() != digest.removeprefix('sha256:'):
                findings.append({'code': 'managed-file-drift', 'path': relative})
    workflows = list((repo / '.github/workflows').glob('*.yml')) + list((repo / '.github/workflows').glob('*.yaml'))
    # This is source evidence only. Required-check rules and run results need
    # GitHub observations; a matching string is not a successful CI receipt.
    gate_commands = ('project/governance-check.sh', '.governance/governance_check.py',
                     'wellmanifest_governance.py')
    gate_workflows = [str(p.relative_to(repo)) for p in workflows
                      if any(command in p.read_text() for command in gate_commands)]
    if not gate_workflows:
        findings.append({'code': 'governance-ci-invocation-not-found'})
    return {'repository': str(repo), 'precommit': str(hook),
            'precommitExecutable': hook.is_file() and os.access(hook, os.X_OK),
            'originalPrecommit': str(original_hook),
            'managedPinPresent': lock is not None, 'gateWorkflowCandidates': gate_workflows,
            'remoteProtection': 'not-observed', 'hookBehavior': 'not-executed', 'findings': findings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    records, errors, seen = [], [], set()
    for repo in audit.repositories(args.root.resolve()):
        try:
            common = git(repo, 'rev-parse', '--path-format=absolute', '--git-common-dir')
            if common in seen:
                continue
            seen.add(common)
            records.append(observe(repo))
        except (OSError, ValueError, KeyError) as exc:
            errors.append({'repository': str(repo), 'error': str(exc)})
    print(json.dumps({'schema': 'maskservice.enforcement-observation/v1', 'readOnly': True,
                      'repositories': records, 'errors': errors}, indent=2))
    return int(not records or bool(errors) or any(r['findings'] for r in records))


if __name__ == '__main__':
    raise SystemExit(main())
