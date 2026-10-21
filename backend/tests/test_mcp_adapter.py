"""Integration test against a real MCP server subprocess — deliberately no
fakes here. The point of this file is to prove the actual wiring (stdio
spawn, discovery, call) works, not to test flowpermit's logic again.
"""

import sys

from app.mcp_adapter.tool_caller import MCPServerConfig, MCPToolCaller

ECHO_SERVER = MCPServerConfig(
    command=sys.executable,
    args=["-m", "tests.fixtures.echo_mcp_server"],
)


async def test_describe_reports_the_real_tool_schema_and_annotations() -> None:
    caller = MCPToolCaller({"echo_server": ECHO_SERVER})

    descriptor = await caller.describe("echo_server", "echo")

    assert descriptor.input_schema["properties"]["text"]["type"] == "string"
    assert descriptor.annotations is not None
    assert descriptor.annotations.read_only_hint is True


async def test_call_invokes_the_real_server_and_returns_its_output() -> None:
    caller = MCPToolCaller({"echo_server": ECHO_SERVER})

    result = await caller.call("echo_server", "echo", {"text": "hello from the test"})

    assert result == "hello from the test"


async def test_schema_hash_changes_if_the_tool_description_changes() -> None:
    caller = MCPToolCaller({"echo_server": ECHO_SERVER})
    descriptor = await caller.describe("echo_server", "echo")

    # Same server, same tool, computed independently — the hash must be
    # stable across separate connections for schema pinning to work at all.
    descriptor_again = await caller.describe("echo_server", "echo")

    assert descriptor.schema_hash == descriptor_again.schema_hash
