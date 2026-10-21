"""NodeEmitter: turns one IR node into its generated function. Adding a node
type means adding one emitter here and registering it — nothing else in the
generator changes.
"""

from typing import Protocol

from app.core.ir.normalize import SupportedNode


class NodeEmitter(Protocol):
    def imports(self) -> list[tuple[str, str]]:
        """Each item is (module, name) — the generator groups these by
        module so two node types importing from the same place produce one
        `from module import a, b` line, not two."""
        ...

    def render(self, node: SupportedNode) -> str: ...


class AgentEmitter:
    def imports(self) -> list[tuple[str, str]]:
        return [("app.runs.node_runtime", "run_agent_node")]

    def render(self, node: SupportedNode) -> str:
        return (
            f"async def {node.id}(state: FlowState) -> dict[str, Any]:\n"
            f"    return await run_agent_node({node.id!r}, state)\n"
        )


class MCPToolEmitter:
    def imports(self) -> list[tuple[str, str]]:
        return [("app.runs.node_runtime", "run_mcp_tool_node")]

    def render(self, node: SupportedNode) -> str:
        return (
            f"async def {node.id}(state: FlowState) -> dict[str, Any]:\n"
            f"    return await run_mcp_tool_node({node.id!r}, state)\n"
        )


EMITTERS: dict[str, NodeEmitter] = {
    "agent": AgentEmitter(),
    "mcp_tool": MCPToolEmitter(),
}
