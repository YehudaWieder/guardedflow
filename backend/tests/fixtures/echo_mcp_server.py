"""A minimal real MCP server for the mcp_adapter integration test and Part
B's end-to-end demo: one read-only tool. Run standalone as a subprocess:
`python -m tests.fixtures.echo_mcp_server`.
"""

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

server = MCPServer(name="echo_test_server")


@server.tool(annotations=ToolAnnotations(read_only_hint=True))
def echo(text: str) -> str:
    """Echoes the given text back."""
    return text


if __name__ == "__main__":
    server.run(transport="stdio")
