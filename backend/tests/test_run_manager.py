"""End-to-end: GraphDocument -> IR -> generated code -> LangGraph execution,
with a real MCP server and the scripted chat model. This is the full Phase 1
vertical slice, minus the HTTP/SSE layer.
"""

import sys

from app.core.llm.scripted_model import ScriptedChatModel
from app.core.schemas import GraphDocument
from app.mcp_adapter.tool_caller import MCPServerConfig, MCPToolCaller
from app.runs.context import RunContext
from app.runs.manager import run_flow
from flowpermit import InMemoryAuditLog
from tests.fakes.approval import FakeApprovalHandler

ECHO_SERVER = MCPServerConfig(command=sys.executable, args=["-m", "tests.fixtures.echo_mcp_server"])


def _flow_doc(schema_hash: str) -> GraphDocument:
    return GraphDocument.model_validate(
        {
            "schema_version": 1,
            "name": "agent_then_echo",
            "entry": "draft",
            "nodes": [
                {
                    "type": "agent",
                    "id": "draft",
                    "label": "Draft",
                    "position": {"x": 0, "y": 0},
                    "model": "scripted",
                    "system_prompt": "be helpful",
                    "input_template": "say hi",
                },
                {
                    "type": "mcp_tool",
                    "id": "send",
                    "label": "Echo",
                    "position": {"x": 0, "y": 0},
                    "server_id": "echo_server",
                    "tool_name": "echo",
                    "arguments": {"text": "{{outputs.draft.text}}"},
                    "tool_policy_id": "demo_policy",
                },
            ],
            "edges": [{"id": "e1", "source": "draft", "target": "send"}],
            "policies": [
                {
                    "id": "demo_policy",
                    "grants": [
                        {
                            "server_id": "echo_server",
                            "tool": "echo",
                            "schema_hash": schema_hash,
                            "approval": "never",
                            "max_calls_per_run": 5,
                        }
                    ],
                }
            ],
        }
    )


async def test_runs_a_full_flow_end_to_end_against_a_real_mcp_server() -> None:
    caller = MCPToolCaller({"echo_server": ECHO_SERVER})
    schema_hash = (await caller.describe("echo_server", "echo")).schema_hash
    doc = _flow_doc(schema_hash)

    context = RunContext(
        run_id="run_e2e",
        model=ScriptedChatModel(["hello from the agent"]),
        approval_handler=FakeApprovalHandler(),
        audit_log=InMemoryAuditLog(),
    )

    final_state = await run_flow(doc, context, mcp_servers={"echo_server": ECHO_SERVER})

    assert final_state["outputs"]["draft"]["text"] == "hello from the agent"
    assert (
        final_state["outputs"]["send"]["text"]
        == "<tool_output>\nhello from the agent\n</tool_output>"
    )

    event_kinds = [event.kind for event in context.events]
    assert event_kinds == [
        "node_started",
        "node_completed",
        "node_started",
        "tool_requested",
        "node_completed",
        "run_finished",
    ]
    assert context.events[-1].status == "ok"
    assert [event.seq for event in context.events] == list(range(1, len(context.events) + 1))
    assert context.audit_log.verify() is True


async def test_run_fails_loudly_when_the_policy_has_a_stale_schema_hash() -> None:
    doc = _flow_doc("sha256:stale")
    context = RunContext(
        run_id="run_fail",
        model=ScriptedChatModel(["hello"]),
        approval_handler=FakeApprovalHandler(),
        audit_log=InMemoryAuditLog(),
    )

    try:
        await run_flow(doc, context, mcp_servers={"echo_server": ECHO_SERVER})
        raise AssertionError("expected run_flow to raise")
    except Exception:
        pass

    assert context.events[-1].kind == "run_finished"
    assert context.events[-1].status == "failed"
    assert any(event.kind == "tool_blocked" for event in context.events)
