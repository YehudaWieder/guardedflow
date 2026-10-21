"""Shared execution logic that every generated nodes.py calls into.
Generated code holds only structure (names, edges) — this is where the
actual work happens: resolving templates, calling the model, and (for
mcp_tool nodes) calling the tool through flowpermit. Node functions are
thin wrappers around these, keyed by node id.
"""

import time
from typing import Any

from app.core.ir.resolver import resolve
from app.core.schemas.events import NodeCompleted, NodeStarted, ToolCallBlocked, ToolCallRequested
from app.runs.context import RunContext
from flowpermit import ToolBlockedError

# Set by the Run Manager before executing a flow — one context per run, not
# constructed per node.
_current_context: RunContext | None = None


def set_run_context(context: RunContext) -> None:
    global _current_context
    _current_context = context


def _require_context() -> RunContext:
    if _current_context is None:
        raise RuntimeError("no RunContext configured for this run")
    return _current_context


async def run_agent_node(node_id: str, state: dict[str, Any]) -> dict[str, Any]:
    ctx = _require_context()
    ctx.record(NodeStarted(run_id=ctx.run_id, seq=0, ts=0, kind="node_started", node_id=node_id))

    config = state["run_meta"]["flow_config"][node_id]
    start = time.monotonic()
    text = await ctx.model.complete(
        system_prompt=config["system_prompt"],
        user_message=resolve(config["input_template"], state["outputs"]),
        temperature=config["temperature"],
        max_tokens=config["max_tokens"],
    )
    latency_ms = int((time.monotonic() - start) * 1000)
    output = {"text": text}
    ctx.record(
        NodeCompleted(
            run_id=ctx.run_id,
            seq=0,
            ts=0,
            kind="node_completed",
            node_id=node_id,
            output=output,
            latency_ms=latency_ms,
        )
    )
    return {"outputs": {node_id: output}}


async def run_mcp_tool_node(node_id: str, state: dict[str, Any]) -> dict[str, Any]:
    ctx = _require_context()
    config = state["run_meta"]["flow_config"][node_id]
    policy_id = config["tool_policy_id"]
    executor = ctx.executors.get(policy_id)
    if executor is None:
        raise RuntimeError(f"no GuardedToolExecutor configured for policy {policy_id!r}")

    ctx.record(NodeStarted(run_id=ctx.run_id, seq=0, ts=0, kind="node_started", node_id=node_id))
    arguments = {
        key: resolve(value, state["outputs"]) for key, value in config["arguments"].items()
    }
    ctx.record(
        ToolCallRequested(
            run_id=ctx.run_id,
            seq=0,
            ts=0,
            kind="tool_requested",
            node_id=node_id,
            tool=config["tool_name"],
            args=arguments,
        )
    )

    start = time.monotonic()
    try:
        output_text = await executor.call_tool(
            node_id=node_id,
            server_id=config["server_id"],
            tool=config["tool_name"],
            arguments=arguments,
        )
    except ToolBlockedError as exc:
        ctx.record(
            ToolCallBlocked(
                run_id=ctx.run_id,
                seq=0,
                ts=0,
                kind="tool_blocked",
                node_id=node_id,
                tool=config["tool_name"],
                reason=exc.reason,
            )
        )
        raise

    latency_ms = int((time.monotonic() - start) * 1000)
    output = {"text": output_text}
    ctx.record(
        NodeCompleted(
            run_id=ctx.run_id,
            seq=0,
            ts=0,
            kind="node_completed",
            node_id=node_id,
            output=output,
            latency_ms=latency_ms,
        )
    )
    return {"outputs": {node_id: output}}
