"""Each check is a pure function from context to a decision — no I/O, no
side effects, each testable alone. GuardedToolExecutor calls these in the
fixed order: grant, schema pin, arguments, budget.
"""

import re
from dataclasses import dataclass
from typing import Any

import jsonschema

from flowpermit.models import ToolGrant, ToolPolicy


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    reason: str | None = None

    @staticmethod
    def allow() -> "CheckResult":
        return CheckResult(ok=True)

    @staticmethod
    def deny(reason: str) -> "CheckResult":
        return CheckResult(ok=False, reason=reason)


def check_grant(
    policy: ToolPolicy, server_id: str, tool: str
) -> tuple[CheckResult, ToolGrant | None]:
    for grant in policy.grants:
        if grant.server_id == server_id and grant.tool == tool:
            return CheckResult.allow(), grant
    return CheckResult.deny(f"no grant for {server_id}/{tool}"), None


def check_schema_pin(grant: ToolGrant, current_schema_hash: str) -> CheckResult:
    if grant.schema_hash != current_schema_hash:
        return CheckResult.deny(
            f"tool schema changed since approval "
            f"(expected {grant.schema_hash}, got {current_schema_hash})"
        )
    return CheckResult.allow()


def check_arguments(
    grant: ToolGrant, arguments: dict[str, Any], input_schema: dict[str, Any]
) -> CheckResult:
    try:
        jsonschema.validate(arguments, input_schema)
    except jsonschema.ValidationError as exc:
        return CheckResult.deny(f"argument schema violation: {exc.message}")

    for rule in grant.arg_rules:
        if rule.arg not in arguments:
            continue
        text = str(arguments[rule.arg])
        if rule.max_length is not None and len(text) > rule.max_length:
            return CheckResult.deny(f"argument {rule.arg!r} exceeds max_length {rule.max_length}")
        if rule.allowed is not None and text not in rule.allowed:
            return CheckResult.deny(f"argument {rule.arg!r} is not in the allowed list")
        if rule.pattern is not None and not re.fullmatch(rule.pattern, text):
            return CheckResult.deny(f"argument {rule.arg!r} does not match the required pattern")
    return CheckResult.allow()


def check_budget(grant: ToolGrant, calls_so_far: int) -> CheckResult:
    if calls_so_far >= grant.max_calls_per_run:
        return CheckResult.deny(f"max_calls_per_run ({grant.max_calls_per_run}) exceeded")
    return CheckResult.allow()
