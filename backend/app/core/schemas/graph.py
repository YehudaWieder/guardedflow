"""GraphDocument: the IR for a flow, as produced by the Canvas and consumed by
both the Run Manager and the code generator. One schema, two destinations.
"""

from typing import Annotated, Any, Literal

from pydantic import ConfigDict, Field

from app.core.schemas.base import StrictModel
from app.core.schemas.policy import ToolPolicy

NODE_ID_PATTERN = r"^[a-z][a-z0-9_]{0,40}$"


class Position(StrictModel):
    x: float
    y: float


class BaseNode(StrictModel):
    id: str = Field(pattern=NODE_ID_PATTERN)
    label: str
    position: Position


class AgentNode(BaseNode):
    type: Literal["agent"] = "agent"
    model: str
    system_prompt: str
    input_template: str
    temperature: float = Field(0.2, ge=0, le=1)
    max_tokens: int = Field(1024, gt=0)
    tool_policy_id: str | None = None
    output_schema: dict[str, Any] | None = None


class MCPToolNode(BaseNode):
    type: Literal["mcp_tool"] = "mcp_tool"
    server_id: str
    tool_name: str
    arguments: dict[str, str]
    tool_policy_id: str


class Condition(StrictModel):
    ref: str
    op: Literal["eq", "ne", "gt", "lt", "contains", "in", "exists"]
    value: str | int | float | bool | list[Any] | None = None


class Route(StrictModel):
    target: str
    match: Literal["all", "any"] = "all"
    conditions: list[Condition]


class RouterNode(BaseNode):
    type: Literal["router"] = "router"
    routes: list[Route]
    default_target: str
    max_iterations: int = 5


class ValidatorNode(BaseNode):
    type: Literal["validator"] = "validator"
    model_config = ConfigDict(populate_by_name=True)

    source: str
    schema_: dict[str, Any] = Field(alias="schema")
    retry_target: str
    max_retries: int = 2


Node = Annotated[
    AgentNode | MCPToolNode | RouterNode | ValidatorNode,
    Field(discriminator="type"),
]


class Edge(StrictModel):
    id: str
    source: str
    target: str


class GraphDocument(StrictModel):
    schema_version: Literal[1] = 1
    name: str
    entry: str
    nodes: list[Node]
    edges: list[Edge]
    policies: list[ToolPolicy] = Field(default_factory=list)
