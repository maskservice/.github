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
All 17 still report absent required status checks; this rollout does not
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
