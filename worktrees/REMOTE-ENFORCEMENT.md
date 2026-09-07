# GitHub enforcement

Host hook installation does not establish server protection. Read the current
applicable rules and classic branch protection from GitHub:

```bash
python3 worktrees/remote_enforcement.py maskservice/c2004 maskservice/update
```

The tool requires authenticated `gh` with permission to read repository
protection. Permission errors, generic 404 responses, invalid JSON and truncated
rule lists are errors, not evidence of either protection or its absence.
Only the explicit `Branch not protected` response denotes absent classic
protection. Required check contexts from both mechanisms are reported together.
Successful check runs and bypass coverage require separate inspection.

To add the baseline history guard to an explicitly named Maskservice repository:

```bash
python3 worktrees/remote_enforcement.py maskservice/c2004 --apply-history-protection
```

This creates `maskservice-default-history`, an active ruleset targeting only
the default branch, with deletion and non-fast-forward restrictions and no
bypass actors. It preserves existing rulesets and accepts an identical existing
policy without mutation. A conflicting named policy is reported for review;
it is never silently replaced. The implementation follows the official
[GitHub repository rules API](https://docs.github.com/en/rest/repos/rules#create-a-repository-ruleset).

This baseline preserves direct-main workflows and feature-branch cleanup.
It does not require PRs or successful product tests. Even after installation,
exit status remains nonzero if required CI checks are absent. This is deliberate:
protecting history is one part of enforcement, not a full compliance result.
Full CI enforcement must use checks appropriate to the repository's publication
workflow; do not invent check contexts or bypass failing checks to turn a report
green.

Local before/after receipts belong in ignored `.subactor/recovery`. The default
command is read-only. Mutation is restricted to explicitly named repositories
in `maskservice`; dependency repositories are observation-only.

## Observed rollout — 2026-09-07

All 17 GitHub Maskservice repositories discovered by exact origin mapping in
the local workspace now have the baseline ruleset. Effective rules were read
back from GitHub after each change. No bypass actors were configured.
At that initial observation, all 17 lacked required status checks; the baseline does not
claim that regression-test enforcement is complete.

| Repository | Active history ruleset |
|---|---|
| maskservice/.github | [View 22435044](https://github.com/maskservice/.github/rules/22435044) |
| maskservice/boardnet-digital-twin | [View 22435081](https://github.com/maskservice/boardnet-digital-twin/rules/22435081) |
| maskservice/c2004 | [View 22435089](https://github.com/maskservice/c2004/rules/22435089) |
| maskservice/c2004-firmware | [View 22435100](https://github.com/maskservice/c2004-firmware/rules/22435100) |
| maskservice/core | [View 22435108](https://github.com/maskservice/core/rules/22435108) |
| maskservice/deploy | [View 22435123](https://github.com/maskservice/deploy/rules/22435123) |
| maskservice/displaynet | [View 22435139](https://github.com/maskservice/displaynet/rules/22435139) |
| maskservice/firmware | [View 22435148](https://github.com/maskservice/firmware/rules/22435148) |
| maskservice/fleet | [View 22435154](https://github.com/maskservice/fleet/rules/22435154) |
| maskservice/maskauth | [View 22435158](https://github.com/maskservice/maskauth/rules/22435158) |
| maskservice/maskservice-digital-twin-lab | [View 22435161](https://github.com/maskservice/maskservice-digital-twin-lab/rules/22435161) |
| maskservice/rp2040-keyboard | [View 22435165](https://github.com/maskservice/rp2040-keyboard/rules/22435165) |
| maskservice/stacknet | [View 22435172](https://github.com/maskservice/stacknet/rules/22435172) |
| maskservice/stacknet-digital-twin | [View 22435176](https://github.com/maskservice/stacknet-digital-twin/rules/22435176) |
| maskservice/update | [View 22435181](https://github.com/maskservice/update/rules/22435181) |
| maskservice/viewer | [View 22435191](https://github.com/maskservice/viewer/rules/22435191) |
| maskservice/workshop | [View 22435197](https://github.com/maskservice/workshop/rules/22435197) |

Validation: 43 local tests passed, including permission errors, empty required
check rules, preservation of unrelated rulesets, idempotence and refusal to
overwrite conflicting policies.

A separate observation found failing `verify` checks on the current BoardNet
and StackNet main commits. BoardNet run [34101532781](https://github.com/maskservice/boardnet-digital-twin/actions/runs/34101532781)
reports `GOV-BASE-002` during the governance pytest gate after integration.
This remains a CI repair item; earlier successful PR checks do not establish
a successful check for the integrated main commit.

## Compare Validator authority before changing required CI

```bash
python3 worktrees/remote_enforcement.py maskservice/boardnet-digital-twin \
  --registry /path/to/validator-agent/config/direct-pr-registry.json
```

Use a trusted, published registry snapshot. The report binds its file digest
and version, applies explicit repository overrides over account defaults, and
reports missing contexts on either side. A policy mismatch exits nonzero;
it must be resolved through protected registry publication. The auditor never
weakens checks or grants approval from a supplied file.

This comparison was added after initial hosted-check activation exposed
`DIRECT_PR_REGISTRY_POLICY_DRIFT`. Protected Validator PR
[#350](https://github.com/subactor/validator-agent/pull/350) adds exact profiles
for the four adopted twin/device repositories, retaining OneDev alongside all
three hosted checks. Registry 1.3.46 was independently approved and merged.
Six repository rule sets were subsequently read back and matched the registry:
BoardNet, StackNet, DisplayNet, Digital Twin Lab, update and viewer. The latter
two use their existing protected OneDev profiles. All six use strict required
checks and no configured bypass actors. Eleven other discovered Maskservice
repositories still require CI adoption compatible with their delivery workflow.


BoardNet [PR #2](https://github.com/maskservice/boardnet-digital-twin/pull/2)
restores GitHub-observed terminal receipts through the managed activity helper
and validates integrated main state without replaying a merged adoption.
The protected Validator approved exact head `012ac3895e061c26205b9e2a0b4559a91550912f`
and merged it as `3f7c8a7e5b3847c313e0c599f48b35bdf0c4fc17`.


StackNet [PR #2](https://github.com/maskservice/stacknet-digital-twin/pull/2)
delivers the same repair, independently approved at
`744fb708fc93e67746c120a116e3256160f0c340` and merged as
`8ee1e354fe64af46fee3319267492cae88652aa2`.
BoardNet's integrated `verify` run
[34106268927](https://github.com/maskservice/boardnet-digital-twin/actions/runs/34106268927)
succeeded, as did StackNet’s integrated run
[34106459217](https://github.com/maskservice/stacknet-digital-twin/actions/runs/34106459217).
Each repair includes five receipt-binding tests and retains all
three product tests and the managed governance gate. Validator's registry
repair passed all 705 tests with pinned dependencies; the shared audit now
passes 46 tests, including policy drift and repository/account inheritance.

The three owned delivery worktrees are released only after exact-head merge
confirmation, clean tracked state, process checks and private preservation of
tracked and ignored data. Original unrelated worktrees remain untouched.
