#!/usr/bin/env python3
"""Install an offline host guard while preserving the clone's previous hooks."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from hook_contract import owns_hook

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
    managed_hook = owns_hook(repo)
    current = subprocess.run(['git', '-C', str(repo), 'config', '--get', 'core.hooksPath'],
                             text=True, capture_output=True).stdout.strip()
    if state_path.exists():
        state = json.loads(state_path.read_text())
        if current != str(hooks) and not (state.get('mode') == 'managed-delegation' and current == state['previousHooksPath']):
            raise ValueError('hooksPath changed since installation; preserve the new owner')
    else:
        if current == str(hooks) or hooks.exists():
            raise ValueError('Unowned hook directory; refusing to replace it')
        state = {'schema': 'maskservice.local-hook-install/v1', 'previousHooksPath': current,
                 'previousDefaultDirectory': str(common / 'hooks'), 'source': str(HERE)}
    # Full managed adoption owns hooksPath exactly. Its host validator must
    # keep seeing the package's original location; an extra wrapper would
    # otherwise introduce a new conformance error even when it forwards calls.
    if managed_hook:
        previous = state['previousHooksPath']
        if current == str(hooks):
            if previous:
                git(repo, 'config', '--local', 'core.hooksPath', previous)
            else:
                subprocess.run(['git', '-C', str(repo), 'config', '--local', '--unset', 'core.hooksPath'], check=True)
        if state_path.exists():
            state['mode'] = 'managed-delegation'
            state_path.write_text(json.dumps(state, indent=2) + '\n')
        original = Path(previous) if previous else common / 'hooks'
        if not original.is_absolute():
            original = repo / original
        ready = (original / 'pre-commit').is_file() and os.access(original / 'pre-commit', os.X_OK)
        return {'repository': str(repo), 'status': 'managed-delegation',
                'originalHook': str(original / 'pre-commit'), 'managedHookExecutable': ready}
    state['mode'] = 'composed'
    snapshot = common / 'maskservice-placement-guard'
    snapshot.mkdir(exist_ok=True)
    for name in ('precommit.py', 'audit.py', 'hook_contract.py', 'repository_policy.py', 'prepush.py'):
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
payload = None
if name == 'pre-push':
    payload = sys.stdin.buffer.read()
    result = subprocess.run([sys.executable, str(common / 'maskservice-placement-guard/prepush.py'), *sys.argv[1:]], input=payload)
    if result.returncode:
        sys.exit(result.returncode)
if name == 'pre-commit':
    result = subprocess.run([sys.executable, str(common / 'maskservice-placement-guard/precommit.py')])
    if result.returncode:
        sys.exit(result.returncode)
previous = Path(state['previousHooksPath']) if state['previousHooksPath'] else Path(state['previousDefaultDirectory'])
if not previous.is_absolute():
    previous = root / previous
hook = previous / name
if hook.is_file() and os.access(hook, os.X_OK):
    if payload is not None:
        sys.exit(subprocess.run([str(hook), *sys.argv[1:]], input=payload).returncode)
    os.execv(str(hook), [str(hook), *sys.argv[1:]])
sys.path.insert(0, str(common / 'maskservice-placement-guard'))
from hook_contract import owns_hook
if name == 'pre-commit' and owns_hook(root):
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
