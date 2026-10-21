"""A fake MCP tool caller for flowpermit tests — not a mock: it has real
(if simplified) behavior, so tests exercise flowpermit's actual logic
against it rather than asserting on which methods were called.
"""

from typing import Any

from flowpermit.executor import ToolDescriptor
from flowpermit.risk import ToolAnnotations


class FakeToolCaller:
    def __init__(
        self,
        *,
        schema_hash: str = "sha256:abc",
        input_schema: dict[str, Any] | None = None,
        annotations: ToolAnnotations | None = None,
        output: object = "ok",
    ) -> None:
        self.schema_hash = schema_hash
        self.input_schema = input_schema or {"type": "object", "properties": {}}
        self.annotations = annotations
        self.output = output
        self.calls: list[tuple[str, str, dict[str, Any]]] = []

    async def describe(self, server_id: str, tool: str) -> ToolDescriptor:
        return ToolDescriptor(
            schema_hash=self.schema_hash,
            input_schema=self.input_schema,
            annotations=self.annotations,
        )

    async def call(self, server_id: str, tool: str, arguments: dict[str, Any]) -> object:
        self.calls.append((server_id, tool, arguments))
        return self.output
