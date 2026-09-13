# MCP for Maskservice refactoring

Generate workspace overrides with a Python environment that contains the MCP
client SDK. The Semcod and Autogrammar checkouts must be siblings of Maskservice.

```bash
python mcp/workspace_profile.py /path/to/github/maskservice --install
python mcp/smoke.py /path/to/github/maskservice worktrees \
  --output .subactor/receipts/mcp-smoke.json
python -m unittest discover -s mcp
```

Run these commands from the `.github` checkout. `--install` creates the local
workspace `.codex/config.toml` exclusively; an existing file is never overwritten.
Without `--install`, review the TOML on stdout and merge existing settings manually.
The generator copies no global credentials. Reload the MCP client to use the new
profile; already running servers retain their old environment and Python imports.
Codex loads project settings only for trusted projects; see the
[official MCP configuration documentation](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).

Code2LLM and Code2Logic are confined to the explicit Maskservice root. Pass a
bounded source directory, not the entire workspace with its historical worktrees.
The smoke test initializes fresh MCP transports, enumerates their tools, analyzes
real code, and verifies that the two confined analyzers reject the parent path.
It also generates an NLP2CMD plan without executing it, scans with reDUP, checks
all three NLP2DSL services, and verifies rejection of an invalid workflow.
It exits nonzero on a missing dependency, missing tool, empty code scan or failed
contract. Raw results can contain local paths and belong in ignored receipts.

## Local runtime repair

The 2026-09-13 NLP2CMD repair used `nlp2cmd-intent==0.1.2`,
`pact-ir==0.1.0` and `nlp2cmd-planner==0.1.2`. The previous environment had stale
or broken installations. Verify imports in a fresh process after changing them;
package metadata alone was insufficient evidence of availability.

The NLP2DSL legacy Compose file publishes NLP on **8012**, backend on 8010 and
worker on 8004. Specify the file explicitly: plain `docker compose` selects the
different `compose.yml`, which has no `nlp-service` service.
Its NLP image omits `env2llm` and two local DSL packages. This adapter installs
them and imports the complete application during build so missing imports fail
before service replacement. From the NLP2DSL checkout:

```bash
docker compose -f docker-compose.yml build nlp-service
docker build -f /path/to/maskservice/.github/mcp/nlp2dsl-runtime.Dockerfile \
  -t maskservice/nlp2dsl-nlp-service:mcp .
docker compose -f docker-compose.yml \
  -f /path/to/maskservice/.github/mcp/nlp2dsl-runtime.override.yml \
  up -d --no-deps --no-build nlp-service
```

This is a local deployment adapter, not an upstream source release. Its base
image and local packages come from the observed NLP2DSL checkout. Record their
revisions/image identity with deployment evidence. Upstream should incorporate
these dependencies into its own image and lock its transitive requirements.
No LLM provider credentials are required for health and rule-based validation.

## Interpret results

Transport success is distinct from conformance. FastMCP may wrap payloads under
`result`, including JSON strings. Intract can return `success: true` with
`status: partial`; VALLM can return `success: true` with `verdict: fail`; SUMD
and NLP2DSL can reject input while MCP `isError` is false. `smoke.py` normalizes
the observed wrappers and negative verdicts, then applies tool-specific evidence
requirements. It is not a universal semantic verifier or a replacement for
project tests, managed governance gates or independent publication review.

reDUP exact detection works without optional embedding packages. Cross-component
duplicates require ownership review. Code2Logic's duplicate detector hashes
names and signatures, not function bodies: its matches are candidates, never
proof of equivalent behavior. Intract needs concrete contracts; an empty set of
matches does not establish requirements coverage.
