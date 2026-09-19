#!/usr/bin/env python3
"""Inventory actual Wellmanifest pins and update wiring; never infer CI success."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import subprocess


def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


def read(root, path):
    file = root / path
    return json.loads(file.read_text()) if file.is_file() else {}


def collect_pins(root):
    """Read adoption evidence and check managed bytes without Git or network effects."""
    pins, findings = [], []

    def pin(package, revision, version, source, kind):
        pins.append(dict(package=package, revision=revision, version=version,
                         source=source, kind=kind))

    lock = read(root, '.governance/manifest.lock.json')
    standard = lock.get('standard', {})
    if standard:
        pin(standard['id'], standard['sourceRevision'], standard['version'],
            '.governance/manifest.lock.json', 'managed')
        for path, digest in lock.get('managedFiles', {}).items():
            target = root / path
            if (not target.resolve().is_relative_to(root) or not target.is_file()
                    or target.is_symlink()
                    or hashlib.sha256(target.read_bytes()).hexdigest() != digest.removeprefix('sha256:')):
                findings.append(dict(code='managed-artifact-drift', path=path))
    for name, item in read(root, '.governance/wellmanifest.lock.json').get('packages', {}).items():
        pin(item['repository'], item['revision'], item['version'],
            '.governance/wellmanifest.lock.json', 'vendored')
    vendor = read(root, 'worktrees/vendor/source.json')
    if vendor:
        pin(vendor['repository'], vendor['revision'], vendor['version'],
            'worktrees/vendor/source.json', 'vendored')
    for item in read(root, 'standards/standards-lock.json').get('standards', []):
        pin(item['id'], item.get('sourceRevision'), item.get('version'),
            'standards/standards-lock.json', item.get('status', 'declared'))
    for item in read(root, '.wellmanifest/adoption.json').get('standards', []):
        pin(item['id'], item['revision'], item['version'],
            '.wellmanifest/adoption.json', item.get('status', 'declared'))
        if item['id'] == standard.get('id') and (
                item['revision'] != standard['sourceRevision'] or item['version'] != standard['version']):
            findings.append(dict(code='adoption-metadata-disagrees-with-lock', package=item['id']))
    for pack in ('pcb', 'sch'):
        path = f'app/standards/wellmanifest-{pack}.standard.json'
        item = read(root, path)
        if item:
            pin(f'wellmanifest/{pack}', None, item['version'], path, 'vendored-unpinned')

    return pins, findings


def update_wiring(root, tracked):
    """Observe scheduled checks and the effective hook, not successful execution."""
    workflows = {path: (root / path).read_text() for path in tracked
                 if path.startswith('.github/workflows/') and path.endswith(('.yml', '.yaml'))
                 and (root / path).is_file()}
    freshness = [path for path, text in workflows.items()
                 if 'schedule:' in text and (
                     ('governance adopt' in text and '--latest' in text)
                     or ('standards.py' in text and '--remote' in text)
                     or 'refresh_standard.py' in text
                     or ('wellmanifest.lock.json' in text and '/releases/latest' in text))]
    hook_path = Path(git(root, 'rev-parse', '--path-format=absolute', '--git-path', 'hooks/pre-commit'))
    hook = hook_path.read_text() if hook_path.is_file() else ''
    policy = read(root, '.governance/standard-adoption.json').get('updates', {})
    hook_update = bool(policy.get('enabled') and 'run_standard_update_controller' in hook)
    return hook_update, freshness


def observe(root):
    root = Path(root).resolve()
    tracked = set(git(root, 'ls-files').splitlines())
    pins, findings = collect_pins(root)
    hook_update, freshness = update_wiring(root, tracked)
    refs = git(root, 'grep', '-l', '-i', 'wellmanifest', '--', 'AGENTS.md') if 'AGENTS.md' in tracked and 'wellmanifest' in (root / 'AGENTS.md').read_text().lower() else ''
    return dict(repository=root.name, head=git(root, 'rev-parse', 'HEAD'),
                workingTreeDirty=bool(git(root, 'status', '--porcelain')), pins=pins,
                adoption='artifacts' if pins else 'instructions-only' if refs else 'not-detected',
                precommitUpdateController=hook_update, scheduledFreshness=freshness,
                automaticPublication='not-established', remoteEnforcement='not-observed', findings=findings)


def remote(package):
    result = subprocess.run(['gh', 'api', f'repos/{package}/releases/latest'],
                            capture_output=True, text=True)
    if result.returncode:
        return {'status': 'no-final-release' if 'HTTP 404' in result.stderr else 'observation-failed'}
    release = json.loads(result.stdout)
    if release.get('draft') or release.get('prerelease') or not release.get('published_at'):
        return {'status': 'observation-failed'}
    result = subprocess.run(['gh', 'api', f'repos/{package}/commits/{release["tag_name"]}',
                             '--jq', '.sha'], capture_output=True, text=True)
    if result.returncode:
        return {'status': 'observation-failed'}
    return dict(status='final-release', tag=release['tag_name'], revision=result.stdout.strip(),
                publishedAt=release['published_at'], url=release['html_url'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--remote', action='store_true', help='Observe final GitHub releases with gh')
    parser.add_argument('--strict', action='store_true', help='Fail on drift, stale published pins or unavailable observations')
    args = parser.parse_args()
    roots = [args.root] if (args.root / '.git').exists() else sorted(
        p for p in args.root.iterdir() if not p.is_symlink() and (p / '.git').exists())
    records, errors = [], []
    for root in roots:
        try:
            records.append(observe(root))
        except (OSError, ValueError, KeyError, subprocess.CalledProcessError):
            errors.append(dict(repository=root.name, code='local-observation-failed'))
    upstream = {p: remote(p) for p in sorted({pin['package'] for r in records for pin in r['pins']})} if args.remote else {}
    for record in records:
        for pin in record['pins']:
            current = upstream.get(pin['package'], {})
            pin['freshness'] = ('not-observed' if not current else
                                current['status'] if current['status'] != 'final-release' else
                                'matches-final-release' if pin['revision'] == current['revision'] else
                                'differs-from-final-release')
    print(json.dumps(dict(schema='maskservice.standards-audit/v1', readOnly=True,
                          observedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                          scope='explicit repository or immediate Git checkouts; nested submodules excluded',
                          repositories=records, upstream=upstream, errors=errors), indent=2))
    return int(bool(errors) or args.strict and any(r['findings'] or any(
        p['freshness'] in ('differs-from-final-release', 'observation-failed')
        for p in r['pins']) for r in records))


if __name__ == '__main__':
    raise SystemExit(main())
