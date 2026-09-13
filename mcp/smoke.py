#!/usr/bin/env python3
"""Read-only MCP contract probes; never execute generated NLP commands."""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.exceptions import McpError

from workspace_profile import servers


def payload(result):
    if result.structuredContent is not None:
        value = result.structuredContent
    else:
        text = "\n".join(item.text for item in result.content if item.type == "text")
        try:
            value = json.loads(text)
        except ValueError:
            return text
    while isinstance(value, dict) and set(value) == {"result"}:
        value = value["result"]
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except ValueError:
                break
    return value


def accepted(result) -> bool:
    """Transport success alone is not a tool or conformance verdict."""
    value = payload(result)
    if result.isError:
        return False
    if isinstance(value, dict):
        if any(value.get(key) is False for key in ("success", "ok", "valid", "passed", "can_execute")):
            return False
        if value.get("error") or value.get("plan_error"):
            return False
        if value.get("verdict") in ("fail", "error"):
            return False
        if value.get("status") in ("partial", "violation", "fail", "error", "validation_failed", "blocked"):
            return False
    return True


async def probe(name: str, config: dict, target: Path, outside: Path) -> dict:
    observations = []
    async with asyncio.timeout(120):
        async with stdio_client(StdioServerParameters(**config)) as (read, write):
            async with ClientSession(read, write) as session:
                initialized = await session.initialize()
                listed = await session.list_tools()
                available = {tool.name for tool in listed.tools}

                async def call(tool, args):
                    if tool not in available:
                        raise ValueError(f"Missing MCP tool: {tool}")
                    result = await session.call_tool(tool, args)
                    observations.append({"tool": tool, "arguments": args,
                                         "accepted": accepted(result), "result": payload(result)})
                    return result

                if name in ("algitex-code2llm", "code2logic"):
                    tool = "analyze_project" if name == "algitex-code2llm" else "suggest_refactoring"
                    result = await call(tool, {"path": str(target)})
                    good = accepted(result)
                    if name == "algitex-code2llm":
                        good = good and payload(result).get("total_files", 0) > 0
                    else:
                        good = good and "Issues found:" in str(payload(result))
                    try:
                        rejected = await call(tool, {"path": str(outside)})
                        boundary = not accepted(rejected) and "PROJECT_ROOT" in str(payload(rejected))
                    except McpError as error:
                        boundary = "PROJECT_ROOT" in str(error)
                        observations.append({"tool": tool, "arguments": {"path": str(outside)},
                                             "accepted": False, "rpc_error": str(error)})
                    good = good and boundary
                elif name == "nlp2cmd":
                    result = await call("nlp2cmd_analyze", {"query": "list files", "include_plan": True})
                    value = payload(result)
                    good = accepted(result) and isinstance(value, dict) and bool(value.get("intent_ir")) and bool(value.get("execution_plan_ir", {}).get("steps"))
                elif name == "nlp2dsl":
                    result = await call("nlp2dsl_health", {})
                    value = payload(result)
                    if isinstance(value, dict) and "result" in value:
                        value = json.loads(value["result"])
                    good = accepted(result) and isinstance(value, dict) and all(
                        isinstance(value.get(key), dict) and value[key].get("status") == "ok"
                        for key in ("backend", "nlp_service", "worker"))
                    rejected = await call("nlp2dsl_validate", {"workflow_json": "{}"})
                    good = good and not accepted(rejected) and "dsl.steps_invalid" in str(payload(rejected))
                else:
                    result = await call("find_duplicates", {
                        "path": str(target), "extensions": "py", "max_groups": 5,
                        "include_tests": True, "semantic": False, "fuzzy": False,
                        "mode": "standard"})
                    value = payload(result)
                    good = accepted(result) and isinstance(value, dict) and value.get("stats", {}).get("files_scanned", 0) > 0
                return {"server": name, "version": initialized.serverInfo.version,
                        "passed": bool(good), "observations": observations}


async def run(args) -> list:
    config = servers(args.workspace, args.python)
    results = []
    for name in args.servers or config:
        try:
            results.append(await probe(name, config[name], args.target.resolve(), args.workspace.resolve().parent))
        except Exception as error:
            import traceback
            results.append({"server": name, "passed": False,
                            "error": "".join(traceback.format_exception(error))})
    return results


def main() -> None:
    import sys
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("target", type=Path, help="Bounded source directory, not the entire workspace")
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    parser.add_argument("--servers", nargs="+")
    parser.add_argument("--output", type=Path, required=True, help="Use ignored repository-local receipts")
    args = parser.parse_args()
    args.target.resolve(strict=True).relative_to(args.workspace.resolve(strict=True))
    results = asyncio.run(run(args))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n")
    for result in results:
        print(f"{result['server']}: {'PASS' if result['passed'] else 'FAIL'}")
    raise SystemExit(0 if all(result["passed"] for result in results) else 1)


if __name__ == "__main__":
    main()
