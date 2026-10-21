"""The only module that touches the MCP SDK client-side. Implements
flowpermit's ToolCaller protocol: the schema hash is computed here (from
the tool's name, description, and input schema) so flowpermit can pin it
against the hash a human approved.

Each call opens its own stdio connection — simple and correct, at the cost
of a subprocess spawn per call. Session reuse across calls in a run is a
Phase 2+ optimization, not a Phase 1 concern.
"""

import hashlib
import json
from contextlib import AsyncExitStack
from dataclasses import dataclass

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent
from mcp.types import Tool as MCPTool

from flowpermit.executor import ToolDescriptor
from flowpermit.risk import ToolAnnotations


@dataclass(frozen=True)
class MCPServerConfig:
    command: str
    args: list[str]
    env: dict[str, str] | None = None


class MCPToolCaller:
    def __init__(self, servers: dict[str, MCPServerConfig]) -> None:
        self._servers = servers

    async def describe(self, server_id: str, tool: str) -> ToolDescriptor:
        mcp_tool = await self._find_tool(server_id, tool)
        return ToolDescriptor(
            schema_hash=_schema_hash(mcp_tool),
            input_schema=mcp_tool.input_schema,
            annotations=_map_annotations(mcp_tool),
        )

    async def call(self, server_id: str, tool: str, arguments: dict[str, object]) -> str:
        async with self._session(server_id) as session:
            result = await session.call_tool(tool, arguments)
            return "\n".join(
                block.text for block in result.content if isinstance(block, TextContent)
            )

    async def _find_tool(self, server_id: str, tool: str) -> MCPTool:
        async with self._session(server_id) as session:
            listed = await session.list_tools()
            for mcp_tool in listed.tools:
                if mcp_tool.name == tool:
                    return mcp_tool
        raise KeyError(f"server {server_id!r} has no tool named {tool!r}")

    def _session(self, server_id: str) -> "_SessionContext":
        config = self._servers[server_id]
        params = StdioServerParameters(command=config.command, args=config.args, env=config.env)
        return _SessionContext(params)


class _SessionContext:
    """Wraps the nested stdio_client/ClientSession context managers (and the
    required `initialize()` call) behind one `async with`."""

    def __init__(self, params: StdioServerParameters) -> None:
        self._params = params
        self._exit_stack = AsyncExitStack()

    async def __aenter__(self) -> ClientSession:
        stack = self._exit_stack
        read, write = await stack.enter_async_context(stdio_client(self._params))
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        return session

    async def __aexit__(self, *exc_info: object) -> None:
        await self._exit_stack.aclose()


def _schema_hash(tool: MCPTool) -> str:
    payload = json.dumps(
        {"name": tool.name, "description": tool.description, "input_schema": tool.input_schema},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def _map_annotations(tool: MCPTool) -> ToolAnnotations | None:
    if tool.annotations is None:
        return None
    return ToolAnnotations(
        read_only_hint=tool.annotations.read_only_hint,
        destructive_hint=tool.annotations.destructive_hint,
        open_world_hint=tool.annotations.open_world_hint,
    )
