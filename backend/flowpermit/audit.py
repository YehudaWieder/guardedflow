"""Append-only audit log with a SHA-256 hash chain: each record includes the
hash of the one before it, so `verify()` can detect a deleted or altered
entry by recomputing the chain from the start.
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

GENESIS_HASH = "0" * 64


@dataclass(frozen=True)
class AuditRecord:
    seq: int
    ts: str
    run_id: str
    node_id: str
    server_id: str
    tool: str
    arguments: dict[str, Any]
    decision: str
    approver: str | None
    output_hash: str | None
    prev_hash: str

    @property
    def hash(self) -> str:
        payload = json.dumps(
            {
                "seq": self.seq,
                "ts": self.ts,
                "run_id": self.run_id,
                "node_id": self.node_id,
                "server_id": self.server_id,
                "tool": self.tool,
                "arguments": self.arguments,
                "decision": self.decision,
                "approver": self.approver,
                "output_hash": self.output_hash,
                "prev_hash": self.prev_hash,
            },
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode()).hexdigest()


class InMemoryAuditLog:
    """Holds a run's audit trail in memory. A persistent (SQLite-backed) log
    is Phase 2/3 work, once run persistence exists generally — this is the
    same append/verify contract a durable implementation would have."""

    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    def append(
        self,
        *,
        run_id: str,
        node_id: str,
        server_id: str,
        tool: str,
        arguments: dict[str, Any],
        decision: str,
        approver: str | None = None,
        output_hash: str | None = None,
    ) -> AuditRecord:
        prev_hash = self._records[-1].hash if self._records else GENESIS_HASH
        record = AuditRecord(
            seq=len(self._records),
            ts=datetime.now(UTC).isoformat(),
            run_id=run_id,
            node_id=node_id,
            server_id=server_id,
            tool=tool,
            arguments=arguments,
            decision=decision,
            approver=approver,
            output_hash=output_hash,
            prev_hash=prev_hash,
        )
        self._records.append(record)
        return record

    @property
    def records(self) -> list[AuditRecord]:
        return list(self._records)

    def verify(self) -> bool:
        expected_prev = GENESIS_HASH
        for record in self._records:
            if record.prev_hash != expected_prev:
                return False
            expected_prev = record.hash
        return True
