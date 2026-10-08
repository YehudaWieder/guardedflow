"""Tool-call policy: what an agent is allowed to call, and under what conditions.

Enforced at runtime by flowpermit's GuardedToolExecutor — this module only
defines the shape of a policy, not the enforcement logic.
"""

from typing import Literal

from pydantic import Field

from app.core.schemas.base import StrictModel


class ArgRule(StrictModel):
    arg: str
    pattern: str | None = None
    allowed: list[str] | None = None
    max_length: int | None = None


class ToolGrant(StrictModel):
    server_id: str
    tool: str
    schema_hash: str
    approval: Literal["never", "always", "on_risk"] = "on_risk"
    arg_rules: list[ArgRule] = Field(default_factory=list)
    max_calls_per_run: int = 10


class ToolPolicy(StrictModel):
    """A named set of grants. Any server/tool pair not listed here is blocked."""

    id: str
    grants: list[ToolGrant] = Field(default_factory=list)
