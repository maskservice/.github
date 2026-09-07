# Worktrees in Maskservice

Use Wellmanifest Worktrees v5: `<primaryCheckout>/.worktrees/ticket-NNN--slug`,
branch `ticket/NNN-slug`, with the matching lease in
`<primaryCheckout>/.subactor/leases/ticket-NNN--slug.json`.
Resolve the primary checkout through Git, including when starting inside a
linked checkout. Before allocation, validate the layout, reject symlinked
components, acquire the exact runtime lease and feature-probe Git 2.51.0+
for both `worktree add --relative-paths` and `repair --relative-paths`.
Both administrative pointers must be relative.

Root-ignore `/.worktrees/` and each of
`/.subactor/{leases,sessions,recovery,receipts,cache,snapshots}/` separately.
Keep `.subactor/manifest.json` tracked if present. Working data belongs in these
private repository-local namespaces, not `/tmp` or a shared workspace directory.

Repositories with an explicit main-only workflow retain that workflow: this
placement standard does not require creating a worktree when none is needed.
Deployment clones and runtime mirrors must not be relabelled as delivery worktrees.

Run the read-only workspace audit from any directory:

```bash
python3 /path/to/maskservice/.github/worktrees/audit.py /path/to/maskservice
```

Exit 0 means no implemented check failed; exit 1 reports findings or errors.
The audit uses pinned upstream artifacts from the revision in
`vendor/source.json`. It checks registrations, matching branch names, symlinked
layout components, relative pointers, lease file presence, exact ignore rules
and whether the runtime manifest is accidentally ignored. It does not authenticate leases or establish
that work is safe to move or delete. Raw JSON may contain private local paths;
store it in ignored recovery storage, not Git.

Historical registrations require an exact lifecycle audit of dirty and ignored
data, running processes/IDEs, leases, pull requests, unique history and HEAD
reachability before migration. Never automatically move, remove, repair or prune
them. A `prunable` entry is evidence of stale metadata, not deletion authority.

The shared audit is not a replacement for full `new-project` adoption. Repos
that use that package must update its managed files through `goal governance
adopt`, preserving ticket ownership and publication checks.

## Local enforcement and its limits

The policy file is not proof that an agent host enforces it. Run
`python3 worktrees/enforcement.py /path/to/maskservice` to observe effective
Git hook paths, executable hooks, missing or modified managed files, and source
references to the governance CI gate. This audit does not execute arbitrary
hooks, infer successful tests from workflow text, or infer GitHub protection.
Remote rules and exact-head run results require separate observations.

Install the additional offline placement guard for an exact clone:

```bash
python3 worktrees/install_hook.py /path/to/repository
```

The installer records previous configuration in Git's common directory,
packages the pinned checker offline, and composes the original hooks without
rewriting their files. The placement guard rejects commits made from
noncanonical linked worktrees and staged operational data, including forced
adds. It preserves commits from the primary checkout even when unrelated
historical registrations exist. Existing hook failures still block commits.
For a clone with a managed manifest, the installer delegates to its official
hook and preserves its original hooksPath: the managed host validator requires
that exact path. Refreshing a previously composed managed clone restores the
recorded original configuration. Missing managed hooks remain audit failures
and require proper managed adoption; this installer does not fill them with
a partial replacement or claim that commits are blocked in their absence.

This is host installation, not a committed replacement for managed
`new-project` files. Reinstall after updating this package; verify the effective
hook after any other hook installer or checkout relocation. Hook snapshots and
configuration are local and do not follow a clone to another computer. They
apply to Git invocations from any model or editor using that clone, not to
arbitrary filesystem writes. A model that ignores Markdown, `git --no-verify`,
a changed hooksPath or direct API publication requires an independent protected
server boundary. Tests and required deployment receipts remain necessary.

Use repository-local `.subactor` namespaces for operational working files.
System-temporary test fixtures do not become delivery worktrees. Existing
`/tmp` deployment scripts must be migrated by their owning runtime; this
query-only standard neither deletes their data nor rewrites those scripts.
