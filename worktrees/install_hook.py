#!/usr/bin/env python3
"""Install an offline host guard while preserving the clone's previous hooks."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
HOOKS = ('applypatch-msg', 'pre-applypatch', 'post-applypatch', 'pre-commit',
         'pre-merge-commit', 'prepare-commit-msg', 'commit-msg', 'post-commit',
         'pre-rebase', 'post-checkout', 'post-merge', 'pre-push', 'post-rewrite',
         'sendemail-validate', 'pre-auto-gc', 'reference-transaction')


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()


def install(repo):
    repo = Path(repo).resolve()
    common = Path(git(repo, 'rev-parse', '--path-format=absolute', '--git-common-dir'))
    state_path = common / 'maskservice-hook-state.json'
    hooks = common / 'maskservice-hooks'
    current = subprocess.run(['git', '-C', str(repo), 'config', '--get', 'core.hooksPath'],
                             text=True, capture_output=True).stdout.strip()
    if state_path.exists():
        state = json.loads(state_path.read_text())
        if current != str(hooks):
            raise ValueError('hooksPath changed since installation; preserve the new owner')
    else:
        if current == str(hooks) or hooks.exists():
            raise ValueError('Unowned hook directory; refusing to replace it')
        state = {'schema': 'maskservice.local-hook-install/v1', 'previousHooksPath': current,
                 'previousDefaultDirectory': str(common / 'hooks'), 'source': str(HERE)}
    snapshot = common / 'maskservice-placement-guard'
    snapshot.mkdir(exist_ok=True)
    for name in ('precommit.py', 'audit.py'):
        shutil.copyfile(HERE / name, snapshot / name)
    shutil.copytree(HERE / 'vendor', snapshot / 'vendor', dirs_exist_ok=True)
    hooks.mkdir(exist_ok=True)
    # No user hook is overwritten. Forward every supported existing hook with
    # its original arguments, stdin, exit code and execution-bit semantics.
    wrapper = '''#!/usr/bin/env python3
import json, os, subprocess, sys
from pathlib import Path
common = Path(__file__).resolve().parent.parent
state = json.loads((common / 'maskservice-hook-state.json').read_text())
name = Path(__file__).name
root = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip())
if name == 'pre-commit':
    result = subprocess.run([sys.executable, str(common / 'maskservice-placement-guard/precommit.py')])
    if result.returncode:
        sys.exit(result.returncode)
previous = Path(state['previousHooksPath']) if state['previousHooksPath'] else Path(state['previousDefaultDirectory'])
if not previous.is_absolute():
    previous = root / previous
hook = previous / name
if hook.is_file() and os.access(hook, os.X_OK):
    os.execv(str(hook), [str(hook), *sys.argv[1:]])
if name == 'pre-commit' and (root / '.governance/manifest.lock.json').exists():
    print('MASKSERVICE-PRECOMMIT: declared managed pre-commit is missing or not executable; restore adoption before committing', file=sys.stderr)
    sys.exit(1)
'''
    for name in HOOKS:
        path = hooks / name
        path.write_text(wrapper)
        path.chmod(0o755)
    state_path.write_text(json.dumps(state, indent=2) + '\n')
    git(repo, 'config', '--local', 'core.hooksPath', str(hooks))
    return {'repository': str(repo), 'hooksPath': str(hooks),
            'previousHooksPath': state['previousHooksPath'], 'offlineGuard': str(snapshot)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repository', type=Path)
    args = parser.parse_args()
    print(json.dumps(install(args.repository), indent=2))


if __name__ == '__main__':
    main()
