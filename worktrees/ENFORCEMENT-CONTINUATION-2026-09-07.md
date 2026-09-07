# Enforcement continuation — 2026-09-07

The previous observation of 13 missing Wellmanifest hooks was traced to
package versions 0.14–0.17: their locks did not ship a host hook at all.
The installer now distinguishes this legacy adoption from a current package
whose declared hook has disappeared. It uses pinned file declarations as well
as contract presence, so removing a declared file cannot disable ownership.

Legacy adopters receive the additional offline placement guard. Current
adopters retain their official hooksPath and original hooks. Installation
receipts preserve configuration; no managed source was overwritten and no
historical worktree was moved or removed.

After installation, all 39 recursively observed repositories under the local
Maskservice workspace and all 46 observed Wellmanifest repositories have an
executable pre-commit. These counts include nested dependency clones and refer
to this host, not every clone or device. All 85 installation operations completed
without errors. Raw receipts remain under ignored `.subactor/recovery`.

The placement guard additionally rejects removal of already-adopted exact
operational ignore rules. It reads HEAD and the Git index: an unstaged repair
cannot conceal a staged regression. Existing legacy omissions remain audit
findings, rather than blocking unrelated commits indefinitely.

Validation: 33 tests passed, including real Git commits for legacy packages,
existing rejecting hooks, missing declared hooks, configuration handoff,
forced private-file staging, staged ignore removal and noncanonical writers.
The official agent-host validators were also run in all 22 observed clones
that ship them; all 22 passed after installation.

Unresolved full-standard adoption findings:

| Local inventory | Missing package pin | Legacy host contract absent | No recognized governance CI invocation |
|---|---:|---:|---:|
| Maskservice workspace (39) | 34 | 0 | 34 |
| Wellmanifest (46) | 16 | 13 | 26 |

An executable hook is not proof of full package adoption, product-test coverage
or protected publication. The shared guard implements placement and selected
staging checks; it does not replace the official governance gate. Source-level
CI detection is only an observation. No remote protection settings, runtime
application data or deployed UI images were changed in this continuation.
