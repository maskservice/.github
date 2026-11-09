# ERR-MCP-CONTRACT-002: Model Context Protocol Contract Validation Failure

## Description
Occurs when workspace MCP tool schemas or test contracts in `.github/mcp/` fail validation.

## Remediation
1. Run `pytest .github/mcp/test_contracts.py`.
2. Inspect schema drift against expected contracts.
3. Update contracts to conform to `wellmanifest/mcp`.
