"""GuardedToolExecutor: the only thing that calls an MCP tool. Runs the
fixed check order — grant, schema pin, arguments, budget, risk/approval,
execute — and audits the outcome through one exit path, so a block or an
unexpected error is never skipped.
"""

import hashlib
from dataclasses import dataclass
from typing import Any, Protocol

from flowpermit.approval import ApprovalDecision, ApprovalHandler, ApprovalRequest
from flowpermit.audit import InMemoryAuditLog
from flowpermit.checks import check_arguments, check_budget, check_grant, check_schema_pin
from flowpermit.models import ToolGrant, ToolPolicy
from flowpermit.risk import Risk, ToolAnnotations, derive_risk

MAX_OUTPUT_CHARS = 20_000


class ToolBlockedError(Exception):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


@dataclass(frozen=True)
class ToolDescriptor:
    """What the MCP adapter reports about a tool at discovery time."""

    schema_hash: str
    input_schema: dict[str, Any]
    annotations: ToolAnnotations | None


class ToolCaller(Protocol):
    """The actual MCP call, provided by mcp_adapter — flowpermit never
    imports the MCP SDK itself."""

    async def call(self, server_id: str, tool: str, arguments: dict[str, Any]) -> object: ...
    async def describe(self, server_id: str, tool: str) -> ToolDescriptor: ...


class GuardedToolExecutor:
    def __init__(
        self,
        *,
        policy: ToolPolicy,
        caller: ToolCaller,
        approval_handler: ApprovalHandler,
        audit_log: InMemoryAuditLog,
        run_id: str,
    ) -> None:
        self._policy = policy
        self._caller = caller
        self._approval_handler = approval_handler
        self._audit_log = audit_log
        self._run_id = run_id
        self._calls_so_far: dict[tuple[str, str], int] = {}

    async def call_tool(
        self, *, node_id: str, server_id: str, tool: str, arguments: dict[str, Any]
    ) -> str:
        decision = "blocked: unexpected error"
        approver: str | None = None
        output_hash: str | None = None
        audited_arguments = arguments
        try:
            output, approver, audited_arguments = await self._execute(
                node_id, server_id, tool, arguments
            )
            decision = "executed"
            output_hash = hashlib.sha256(output.encode()).hexdigest()
            return output
        except ToolBlockedError as exc:
            decision = f"blocked: {exc.reason}"
            raise
        finally:
            self._audit_log.append(
                run_id=self._run_id,
                node_id=node_id,
                server_id=server_id,
                tool=tool,
                arguments=audited_arguments,
                decision=decision,
                approver=approver,
                output_hash=output_hash,
            )

    async def _execute(
        self, node_id: str, server_id: str, tool: str, arguments: dict[str, Any]
    ) -> tuple[str, str | None, dict[str, Any]]:
        grant_result, grant = check_grant(self._policy, server_id, tool)
        if not grant_result.ok or grant is None:
            raise ToolBlockedError(grant_result.reason or "no grant")

        descriptor = await self._caller.describe(server_id, tool)

        schema_result = check_schema_pin(grant, descriptor.schema_hash)
        if not schema_result.ok:
            raise ToolBlockedError(schema_result.reason or "schema pin mismatch")

        self._require_valid_arguments(grant, arguments, descriptor.input_schema)
        self._require_budget(grant, server_id, tool)

        risk = derive_risk(descriptor.annotations)
        approver: str | None = None
        if grant.approval == "always" or (grant.approval == "on_risk" and risk == "high"):
            arguments, approver = await self._get_approval(
                node_id, server_id, tool, arguments, grant, descriptor, risk
            )

        calls_key = (server_id, tool)
        self._calls_so_far[calls_key] = self._calls_so_far.get(calls_key, 0) + 1
        raw_output = await self._caller.call(server_id, tool, arguments)
        output_text = _delimit_untrusted(_truncate(str(raw_output), MAX_OUTPUT_CHARS))
        return output_text, approver, arguments

    def _require_valid_arguments(
        self, grant: ToolGrant, arguments: dict[str, Any], input_schema: dict[str, Any]
    ) -> None:
        result = check_arguments(grant, arguments, input_schema)
        if not result.ok:
            raise ToolBlockedError(result.reason or "invalid arguments")

    def _require_budget(self, grant: ToolGrant, server_id: str, tool: str) -> None:
        result = check_budget(grant, self._calls_so_far.get((server_id, tool), 0))
        if not result.ok:
            raise ToolBlockedError(result.reason or "budget exceeded")

    async def _get_approval(
        self,
        node_id: str,
        server_id: str,
        tool: str,
        arguments: dict[str, Any],
        grant: ToolGrant,
        descriptor: ToolDescriptor,
        risk: Risk,
    ) -> tuple[dict[str, Any], str]:
        decision: ApprovalDecision = await self._approval_handler.request(
            ApprovalRequest(
                run_id=self._run_id,
                node_id=node_id,
                server_id=server_id,
                tool=tool,
                arguments=arguments,
                reason=f"risk={risk}, approval={grant.approval}",
            )
        )
        if not decision.approved:
            raise ToolBlockedError("approval denied")
        if decision.edited_arguments is not None:
            arguments = decision.edited_arguments
            self._require_valid_arguments(grant, arguments, descriptor.input_schema)
            self._require_budget(grant, server_id, tool)
        return arguments, "human"


def _truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - len("...[truncated]")] + "...[truncated]"


def _delimit_untrusted(text: str) -> str:
    return f"<tool_output>\n{text}\n</tool_output>"
