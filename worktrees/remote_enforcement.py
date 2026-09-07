#!/usr/bin/env python3
"""Audit GitHub enforcement; optionally add non-destructive history protection."""
import argparse
import json
import re
import subprocess
from urllib.parse import quote

NAME = 'maskservice-default-history'
POLICY = {'name': NAME, 'target': 'branch', 'enforcement': 'active',
          'bypass_actors': [],
          'conditions': {'ref_name': {'include': ['~DEFAULT_BRANCH'], 'exclude': []}},
          'rules': [{'type': 'deletion'}, {'type': 'non_fast_forward'}]}


class ApiError(RuntimeError):
    pass


def api(endpoint, method='GET', body=None):
    args = ['gh', 'api', '--method', method, endpoint]
    if body is not None:
        args += ['--input', '-']
    result = subprocess.run(args, input=json.dumps(body) if body is not None else None,
                            text=True, capture_output=True, timeout=60)
    try:
        data = json.loads(result.stdout)
    except ValueError as exc:
        raise ApiError(f'Invalid API response for {endpoint}') from exc
    if result.returncode:
        # Only this explicit response proves absence. Generic 404/403/network
        # failures are unknown, never evidence of a compliant configuration.
        if data.get('status') == '404' and data.get('message') == 'Branch not protected':
            return None
        raise ApiError(f"{endpoint}: {data.get('message', 'API request failed')}")
    return data


def summarize(rules, classic):
    kinds = {r['type'] for r in rules}
    contexts = []
    for rule in rules:
        if rule['type'] == 'required_status_checks':
            contexts.extend(x['context'] for x in rule.get('parameters', {}).get('required_status_checks', []))
    if classic:
        checks = classic.get('required_status_checks') or {}
        contexts.extend(checks.get('contexts', []))
        contexts.extend(x['context'] for x in checks.get('checks', []))
    history = {
        'deletion': 'deletion' in kinds or bool(classic and classic.get('allow_deletions', {}).get('enabled') is False),
        'nonFastForward': 'non_fast_forward' in kinds or bool(classic and classic.get('allow_force_pushes', {}).get('enabled') is False)}
    findings = []
    if not history['deletion']:
        findings.append('default-branch-deletion-not-protected')
    if not history['nonFastForward']:
        findings.append('default-branch-force-push-not-protected')
    if not contexts:
        findings.append('required-status-checks-missing')
    return {'historyProtection': history, 'requiredCheckContexts': sorted(set(contexts)),
            'findings': findings, 'checkRunResults': 'not-observed',
            'bypassCoverage': 'inspect ruleset bypass actors and classic enforce_admins'}


def observe(repository, request=api):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Expected OWNER/REPOSITORY')
    prefix = f'repos/{repository}'
    info = request(prefix)
    branch = info['default_branch']
    rules = request(f'{prefix}/rules/branches/{quote(branch, safe="")}?per_page=100')
    if len(rules) >= 100:
        raise ApiError('Rule response may be truncated; refusing incomplete observation')
    classic = request(f'{prefix}/branches/{quote(branch, safe="")}/protection')
    return {'repository': repository, 'defaultBranch': branch,
            'rules': rules, 'classicProtection': classic, **summarize(rules, classic)}


def protect_history(repository, request=api):
    if not re.fullmatch(r'maskservice/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Mutation is restricted to explicitly named Maskservice repositories')
    prefix = f'repos/{repository}'
    info = request(prefix)
    if info.get('archived') or not info.get('permissions', {}).get('admin'):
        raise ValueError('Repository must be writable with administrative permission')
    existing = request(f'{prefix}/rulesets?per_page=100')
    if len(existing) >= 100:
        raise ApiError('Ruleset response may be truncated')
    matches = [r for r in existing if r['name'] == NAME]
    if matches:
        if len(matches) != 1 or matches[0].get('source') != repository:
            raise ValueError('Ambiguous ruleset ownership; preserve existing configuration')
        detail = request(f"{prefix}/rulesets/{matches[0]['id']}")
        if any(detail.get(key) != value for key, value in POLICY.items()):
            raise ValueError('Existing history policy differs; refusing to overwrite it')
        return {'action': 'unchanged', 'id': detail['id']}
    created = request(f'{prefix}/rulesets', 'POST', POLICY)
    return {'action': 'created', 'id': created['id']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repositories', nargs='+', help='Explicit OWNER/REPOSITORY targets')
    parser.add_argument('--apply-history-protection', action='store_true')
    args = parser.parse_args()
    records = []
    for repository in args.repositories:
        try:
            before = observe(repository)
            change = protect_history(repository) if args.apply_history_protection else None
            after = observe(repository) if change else before
            records.append({'before': before, 'change': change, 'after': after})
        except (ApiError, ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
            records.append({'repository': repository, 'error': str(exc)})
    print(json.dumps({'records': records}, indent=2))
    return int(any('error' in r or r['after']['findings'] for r in records))


if __name__ == '__main__':
    raise SystemExit(main())
