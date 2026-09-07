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
`vendor/source.json`. It checks registrations, relative pointers, lease file
presence and exact ignore rules. It does not authenticate leases or establish
that work is safe to move or delete. Raw JSON may contain private local paths;
store it in ignored recovery storage, not Git.

Historical registrations require an exact lifecycle audit of dirty and ignored
data, running processes/IDEs, leases, pull requests, unique history and HEAD
reachability before migration. Never automatically move, remove, repair or prune
them. A `prunable` entry is evidence of stale metadata, not deletion authority.

The shared audit is not a replacement for full `new-project` adoption. Repos
that use that package must update its managed files through `goal governance
adopt`, preserving ticket ownership and publication checks.
