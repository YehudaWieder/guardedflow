"""End-to-end: flowpermit's GuardedToolExecutor driving the real MCP
adapter against the real echo server subprocess. No fakes anywhere in this
file — this is the proof that the pieces built separately actually work
wired together.
"""

import sys

import pytest

from app.mcp_adapter.tool_caller import MCPServerConfig, MCPToolCaller
from flowpermit import (
    GuardedToolExecutor,
    InMemoryAuditLog,
    ToolBlockedError,
    ToolGrant,
    ToolPolicy,
)
from tests.fakes.approval import FakeApprovalHandler

ECHO_SERVER = MCPServerConfig(command=sys.executable, args=["-m", "tests.fixtures.echo_mcp_server"])


async def test_guarded_call_against_a_real_mcp_server() -> None:
    caller = MCPToolCaller({"echo_server": ECHO_SERVER})
    real_schema_hash = (await caller.describe("echo_server", "echo")).schema_hash

    policy = ToolPolicy(
        id="demo_policy",
        grants=[
            ToolGrant(
                server_id="echo_server",
                tool="echo",
                schema_hash=real_schema_hash,
                approval="never",
                max_calls_per_run=5,
            )
        ],
    )
    audit_log = InMemoryAuditLog()
    executor = GuardedToolExecutor(
        policy=policy,
        caller=caller,
        approval_handler=FakeApprovalHandler(),
        audit_log=audit_log,
        run_id="run_demo",
    )

    result = await executor.call_tool(
        node_id="send_reply", server_id="echo_server", tool="echo", arguments={"text": "hi"}
    )

    assert result == "<tool_output>\nhi\n</tool_output>"
    assert audit_log.records[-1].decision == "executed"
    assert audit_log.verify() is True


async def test_guarded_call_blocked_when_approved_schema_hash_is_stale() -> None:
    caller = MCPToolCaller({"echo_server": ECHO_SERVER})

    policy = ToolPolicy(
        id="demo_policy",
        grants=[
            ToolGrant(
                server_id="echo_server",
                tool="echo",
                schema_hash="sha256:stale-hash-from-a-previous-approval",
                approval="never",
            )
        ],
    )
    executor = GuardedToolExecutor(
        policy=policy,
        caller=caller,
        approval_handler=FakeApprovalHandler(),
        audit_log=InMemoryAuditLog(),
        run_id="run_demo",
    )

    with pytest.raises(ToolBlockedError, match="schema changed"):
        await executor.call_tool(
            node_id="send_reply", server_id="echo_server", tool="echo", arguments={"text": "hi"}
        )
