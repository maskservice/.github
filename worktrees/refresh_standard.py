#!/usr/bin/env python3
"""Refresh the existing Worktrees adoption from a final, annotated GitHub release.

Default is a read-only drift check. --apply updates only the existing artifact
inventory and lock; callers must run their product checks before publication.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def api(path, raw=False):
    args = ['gh', 'api', 'repos/wellmanifest/worktrees/' + path]
    if raw:
        args += ['-H', 'Accept: application/vnd.github.raw+json']
    data = subprocess.run(args, capture_output=True, check=True).stdout
    return data if raw else json.loads(data)


def published():
    release = api('releases/latest')
    tag = release['tag_name']
    if (not re.fullmatch(r'v\d+\.\d+\.\d+', tag) or release['draft']
            or release['prerelease'] or not release['published_at']):
        raise ValueError('A final canonical release is required')
    ref = api('git/ref/tags/' + tag)['object']
    if ref['type'] != 'tag':
        raise ValueError('An annotated release tag is required')
    target = api('git/tags/' + ref['sha'])['object']
    if target['type'] != 'commit' or not re.fullmatch('[0-9a-f]{40}', target['sha']):
        raise ValueError('Tag must resolve directly to an immutable commit')
    return tag[1:], target['sha']


def plan(root, version, revision):
    root = root.resolve()
    lock_path = root / 'worktrees/vendor/source.json'
    if lock_path.is_file():
        lock = json.loads(lock_path.read_text())
        package = lock
        base = root / 'worktrees/vendor'
        entries = package['artifacts']
    else:
        lock_path = root / '.governance/wellmanifest.lock.json'
        lock = json.loads(lock_path.read_text())
        package = lock['packages']['worktrees']
        base = root / '.governance/wellmanifest/worktrees'
        entries = {path: {'sourcePath': path, 'sha256': digest}
                   for path, digest in package['files'].items()}
    if package['repository'] != 'wellmanifest/worktrees':
        raise ValueError('Unexpected owning repository')
    expected = {'operations/conformance.py', 'models/worktrees.schema.json'}
    if {entry['sourcePath'] for entry in entries.values()} != expected or len(entries) != 2:
        raise ValueError('Unexpected artifact inventory')
    for path, entry in entries.items():
        target = base / path
        if (not target.resolve().is_relative_to(root) or target.is_symlink()
                or any(p.is_symlink() for p in target.parents if p.is_relative_to(root))
                or hashlib.sha256(target.read_bytes()).hexdigest() != entry['sha256']):
            raise ValueError('Local artifact drift; preserve and review before refresh')
    if lock_path.is_symlink() or any(p.is_symlink() for p in lock_path.parents if p.is_relative_to(root)):
        raise ValueError('Symlinked lock path')
    changes = {}
    for path, entry in entries.items():
        data = api(f'contents/{entry["sourcePath"]}?ref={revision}', raw=True)
        if (base / path).read_bytes() != data:
            changes[base / path] = data
        entry['sha256'] = hashlib.sha256(data).hexdigest()
    package.update(version=version, revision=revision)
    if 'files' in package:
        package['files'] = {path: entry['sha256'] for path, entry in entries.items()}
    data = (json.dumps(lock, indent=2) + '\n').encode()
    if lock_path.read_bytes() != data:
        changes[lock_path] = data
    return changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        version, revision = published()
        changes = plan(args.root, version, revision)
        for path, data in changes.items():
            if args.apply:
                path.write_bytes(data)
            print(('UPDATED ' if args.apply else 'STALE ') + str(path.relative_to(args.root.resolve())))
        print(f'wellmanifest/worktrees {version} @ {revision}')
        return int(bool(changes) and not args.apply)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f'Refresh refused: {type(error).__name__}; no publication attempted')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
