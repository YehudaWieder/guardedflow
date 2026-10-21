"""Run Manager: turns a GraphDocument into a running flow. It generates the
same code an export would produce, loads it, and executes it through
LangGraph — the platform runs what it would hand you to download.
"""

import json
from typing import Any

from app.codegen.generator import generate_project
from app.core.ir import normalize_graph
from app.core.schemas import GraphDocument, RunFinished
from app.mcp_adapter.tool_caller import MCPServerConfig, MCPToolCaller
from app.runs import node_runtime
from app.runs.context import RunContext
from app.runs.loader import load_generated_graph_module
from flowpermit import GuardedToolExecutor


async def run_flow(
    doc: GraphDocument,
    context: RunContext,
    *,
    mcp_servers: dict[str, MCPServerConfig],
) -> dict[str, Any]:
    """Executes doc under the given RunContext, returning the final
    FlowState. Emits events into context.events throughout, including a
    trailing RunFinished on success or failure. Re-raises after recording a
    failure — the event trail records it, the exception still surfaces."""

    ir = normalize_graph(doc)
    project = generate_project(ir)
    graph_module = load_generated_graph_module(context.run_id, project.files)

    caller = MCPToolCaller(mcp_servers)
    context.executors.update(
        {
            policy.id: GuardedToolExecutor(
                policy=policy,
                caller=caller,
                approval_handler=context.approval_handler,
                audit_log=context.audit_log,
                run_id=context.run_id,
            )
            for policy in doc.policies
        }
    )
    node_runtime.set_run_context(context)

    flow_config = json.loads(project.files["flow_config.json"])
    initial_state: dict[str, Any] = {
        "messages": [],
        "outputs": {},
        "run_meta": {"flow_config": flow_config, "run_id": context.run_id},
    }

    compiled = graph_module.build_graph().compile()
    try:
        final_state: dict[str, Any] = await compiled.ainvoke(initial_state)
    except Exception:
        context.record(
            RunFinished(run_id=context.run_id, seq=0, ts=0, kind="run_finished", status="failed")
        )
        raise

    context.record(
        RunFinished(run_id=context.run_id, seq=0, ts=0, kind="run_finished", status="ok")
    )
    return final_state
