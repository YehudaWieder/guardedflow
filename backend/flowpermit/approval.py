"""ApprovalHandler: the port between flowpermit and whatever can pause a run
for a human decision — `interrupt()` on the platform, a terminal prompt in
an exported project. flowpermit calls this; it doesn't know what's behind it.
"""

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ApprovalRequest:
    run_id: str
    node_id: str
    server_id: str
    tool: str
    arguments: dict[str, Any]
    reason: str


@dataclass(frozen=True)
class ApprovalDecision:
    approved: bool
    edited_arguments: dict[str, Any] | None = None


class ApprovalHandler(Protocol):
    async def request(self, request: ApprovalRequest) -> ApprovalDecision: ...
