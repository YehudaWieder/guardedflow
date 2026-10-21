"""Per-run state that generated nodes.py (via node_runtime) needs: the
model, the guarded executors keyed by policy id, and the event trail. One
instance per run, constructed by the Run Manager and never shared across
runs.
"""

import time
from dataclasses import dataclass, field

from app.core.llm.model_port import ChatModelPort
from app.core.schemas.events import Event
from flowpermit import ApprovalHandler, GuardedToolExecutor, InMemoryAuditLog


@dataclass
class RunContext:
    run_id: str
    model: ChatModelPort
    approval_handler: ApprovalHandler
    audit_log: InMemoryAuditLog
    executors: dict[str, GuardedToolExecutor] = field(default_factory=dict)
    events: list[Event] = field(default_factory=list)
    _seq: int = field(default=0, init=False, repr=False)

    def record(self, event: Event) -> None:
        self._seq += 1
        event.seq = self._seq
        event.ts = time.time()
        self.events.append(event)
