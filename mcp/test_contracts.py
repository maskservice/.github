import json
import tomllib
import unittest
from pathlib import Path

from mcp.types import CallToolResult, TextContent
from workspace_profile import render, servers
from smoke import accepted, payload


class MCPContracts(unittest.TestCase):
    def result(self, value, **kwargs):
        return CallToolResult(content=[TextContent(type="text", text=json.dumps(value))], **kwargs)

    def test_nested_transport_success_cannot_hide_rejection(self):
        for value in ({"success": False}, {"ok": False}, {"valid": False},
                      {"success": True, "verdict": "fail"}, {"plan_error": "missing planner"},
                      {"success": True, "status": "partial"},
                      {"status": "validation_failed", "can_execute": False}):
            with self.subTest(value=value):
                result = self.result({}, structuredContent={"result": value})
                self.assertEqual(payload(result), value)
                self.assertFalse(accepted(result))

    def test_transport_error_overrides_successful_payload(self):
        self.assertFalse(accepted(self.result({"success": True}, isError=True)))

    def test_serialized_fastmcp_result_is_unwrapped(self):
        self.assertEqual(payload(self.result({}, structuredContent={"result": '{"valid": false}'})),
                         {"valid": False})

    def test_project_profile_preserves_scope_and_quoted_paths(self):
        workspace = Path(__file__).resolve().parents[2]
        config = servers(workspace, Path('/runtime with spaces/python'))
        parsed = tomllib.loads(render(config))["mcp_servers"]
        self.assertEqual(parsed, config)
        self.assertEqual(parsed["code2logic"]["env"]["CODE2LOGIC_MCP_PROJECT_ROOT"], str(workspace))
        self.assertEqual(parsed["redup"]["env"]["REDUP_ROOT"], str(workspace))
        self.assertEqual(parsed["nlp2dsl"]["env"]["NLP2DSL_NLP_SERVICE_URL"], 'http://localhost:8012')


if __name__ == "__main__":
    unittest.main()
