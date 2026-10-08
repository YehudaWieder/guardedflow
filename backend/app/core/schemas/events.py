"""Run events: the single record format written to `run_events` and streamed
over SSE. The Trace Panel, equivalence tests, and the audit log all read from
this shape — there is no second event format.
"""

from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field


class EventBase(BaseModel):
    run_id: str
    seq: int
    ts: float


class NodeStarted(EventBase):
    kind: Literal["node_started"]
    node_id: str


class NodeCompleted(EventBase):
    kind: Literal["node_completed"]
    node_id: str
    output: dict[str, Any]
    latency_ms: int


class ToolCallRequested(EventBase):
    kind: Literal["tool_requested"]
    node_id: str
    tool: str
    args: dict[str, Any]


class ToolCallBlocked(EventBase):
    kind: Literal["tool_blocked"]
    node_id: str
    tool: str
    reason: str


class ApprovalRequired(EventBase):
    kind: Literal["approval_required"]
    approval_id: str
    tool: str
    args: dict[str, Any]


class ValidationFailed(EventBase):
    kind: Literal["validation_failed"]
    node_id: str
    errors: list[str]
    attempt: int


class RunFinished(EventBase):
    kind: Literal["run_finished"]
    status: Literal["ok", "failed", "cancelled"]


Event = Annotated[
    NodeStarted
    | NodeCompleted
    | ToolCallRequested
    | ToolCallBlocked
    | ApprovalRequired
    | ValidationFailed
    | RunFinished,
    Field(discriminator="kind"),
]
