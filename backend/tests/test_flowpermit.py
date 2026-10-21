import pytest

from flowpermit import (
    ApprovalDecision,
    ArgRule,
    GuardedToolExecutor,
    InMemoryAuditLog,
    ToolBlockedError,
    ToolGrant,
    ToolPolicy,
)
from flowpermit.risk import ToolAnnotations, derive_risk
from tests.fakes.approval import FakeApprovalHandler
from tests.fakes.tool_caller import FakeToolCaller

READ_ONLY = ToolAnnotations(read_only_hint=True)
DESTRUCTIVE = ToolAnnotations(destructive_hint=True)


def _executor(
    *,
    policy: ToolPolicy,
    caller: FakeToolCaller | None = None,
    approval: FakeApprovalHandler | None = None,
    audit_log: InMemoryAuditLog | None = None,
) -> tuple[GuardedToolExecutor, FakeToolCaller, FakeApprovalHandler, InMemoryAuditLog]:
    caller = caller or FakeToolCaller(annotations=READ_ONLY)
    approval = approval or FakeApprovalHandler()
    audit_log = audit_log or InMemoryAuditLog()
    executor = GuardedToolExecutor(
        policy=policy,
        caller=caller,
        approval_handler=approval,
        audit_log=audit_log,
        run_id="run_1",
    )
    return executor, caller, approval, audit_log


def _grant(**overrides: object) -> ToolGrant:
    defaults: dict[str, object] = {
        "server_id": "srv",
        "tool": "read_file",
        "schema_hash": "sha256:abc",
        "approval": "never",
        "arg_rules": [],
        "max_calls_per_run": 10,
    }
    defaults.update(overrides)
    return ToolGrant.model_validate(defaults)


async def test_blocks_a_call_with_no_grant() -> None:
    policy = ToolPolicy(id="p", grants=[])
    executor, _, _, audit_log = _executor(policy=policy)

    with pytest.raises(ToolBlockedError, match="no grant"):
        await executor.call_tool(node_id="n", server_id="srv", tool="read_file", arguments={})

    assert audit_log.records[-1].decision.startswith("blocked: no grant")


async def test_blocks_a_call_when_the_tool_schema_changed_since_approval() -> None:
    policy = ToolPolicy(id="p", grants=[_grant(schema_hash="sha256:old")])
    caller = FakeToolCaller(schema_hash="sha256:new", annotations=READ_ONLY)
    executor, _, _, _ = _executor(policy=policy, caller=caller)

    with pytest.raises(ToolBlockedError, match="schema changed"):
        await executor.call_tool(node_id="n", server_id="srv", tool="read_file", arguments={})


async def test_blocks_arguments_that_violate_the_input_schema() -> None:
    policy = ToolPolicy(id="p", grants=[_grant()])
    caller = FakeToolCaller(
        annotations=READ_ONLY,
        input_schema={
            "type": "object",
            "required": ["path"],
            "properties": {"path": {"type": "string"}},
        },
    )
    executor, _, _, _ = _executor(policy=policy, caller=caller)

    with pytest.raises(ToolBlockedError, match="argument schema violation"):
        await executor.call_tool(node_id="n", server_id="srv", tool="read_file", arguments={})


async def test_blocks_a_path_traversal_argument() -> None:
    # Negative lookahead rejects ".." anywhere, not just a charset allowlist
    # that would otherwise accept dots and slashes unconditionally.
    grant = _grant(
        arg_rules=[ArgRule(arg="path", pattern=r"(?!.*\.\.)[a-zA-Z0-9_./]+", max_length=100)]
    )
    policy = ToolPolicy(id="p", grants=[grant])
    executor, _, _, _ = _executor(policy=policy)

    with pytest.raises(ToolBlockedError, match="does not match"):
        await executor.call_tool(
            node_id="n", server_id="srv", tool="read_file", arguments={"path": "../../etc/passwd"}
        )


async def test_blocks_once_the_call_budget_is_exhausted() -> None:
    policy = ToolPolicy(id="p", grants=[_grant(max_calls_per_run=2)])
    executor, _, _, _ = _executor(policy=policy)

    await executor.call_tool(node_id="n", server_id="srv", tool="read_file", arguments={})
    await executor.call_tool(node_id="n", server_id="srv", tool="read_file", arguments={})

    with pytest.raises(ToolBlockedError, match="max_calls_per_run"):
        await executor.call_tool(node_id="n", server_id="srv", tool="read_file", arguments={})


async def test_blocks_when_approval_is_denied() -> None:
    policy = ToolPolicy(id="p", grants=[_grant(approval="always")])
    approval = FakeApprovalHandler(ApprovalDecision(approved=False))
    executor, _, _, _ = _executor(policy=policy, approval=approval)

    with pytest.raises(ToolBlockedError, match="approval denied"):
        await executor.call_tool(node_id="n", server_id="srv", tool="read_file", arguments={})


async def test_unclassified_tool_requires_approval_under_on_risk() -> None:
    policy = ToolPolicy(id="p", grants=[_grant(approval="on_risk")])
    caller = FakeToolCaller(annotations=None)  # no annotations at all
    approval = FakeApprovalHandler()
    executor, _, _, _ = _executor(policy=policy, caller=caller, approval=approval)

    await executor.call_tool(node_id="n", server_id="srv", tool="read_file", arguments={})

    assert len(approval.requests) == 1


async def test_read_only_tool_does_not_require_approval_under_on_risk() -> None:
    policy = ToolPolicy(id="p", grants=[_grant(approval="on_risk")])
    caller = FakeToolCaller(annotations=READ_ONLY)
    approval = FakeApprovalHandler()
    executor, _, _, _ = _executor(policy=policy, caller=caller, approval=approval)

    await executor.call_tool(node_id="n", server_id="srv", tool="read_file", arguments={})

    assert len(approval.requests) == 0


async def test_never_approval_skips_approval_even_for_a_destructive_tool() -> None:
    policy = ToolPolicy(id="p", grants=[_grant(approval="never")])
    caller = FakeToolCaller(annotations=DESTRUCTIVE)
    approval = FakeApprovalHandler()
    executor, _, _, _ = _executor(policy=policy, caller=caller, approval=approval)

    await executor.call_tool(node_id="n", server_id="srv", tool="read_file", arguments={})

    assert len(approval.requests) == 0


async def test_server_cannot_downgrade_a_destructive_tool_by_also_claiming_read_only() -> None:
    conflicting = ToolAnnotations(read_only_hint=True, destructive_hint=True)
    assert derive_risk(conflicting) == "high"


async def test_edited_approval_arguments_are_revalidated() -> None:
    grant = _grant(approval="always", arg_rules=[ArgRule(arg="path", pattern=r"[a-z/]+")])
    policy = ToolPolicy(id="p", grants=[grant])
    approval = FakeApprovalHandler(
        ApprovalDecision(approved=True, edited_arguments={"path": "../etc/passwd"})
    )
    executor, _, _, _ = _executor(policy=policy, approval=approval)

    with pytest.raises(ToolBlockedError, match="does not match"):
        await executor.call_tool(
            node_id="n", server_id="srv", tool="read_file", arguments={"path": "ok/path"}
        )


async def test_successful_call_wraps_output_as_untrusted_and_audits_it() -> None:
    policy = ToolPolicy(id="p", grants=[_grant()])
    caller = FakeToolCaller(annotations=READ_ONLY, output="file contents")
    executor, caller, _, audit_log = _executor(policy=policy, caller=caller)

    result = await executor.call_tool(node_id="n", server_id="srv", tool="read_file", arguments={})

    assert result == "<tool_output>\nfile contents\n</tool_output>"
    assert audit_log.records[-1].decision == "executed"
    assert audit_log.records[-1].output_hash is not None


async def test_output_over_the_size_limit_is_truncated() -> None:
    policy = ToolPolicy(id="p", grants=[_grant()])
    caller = FakeToolCaller(annotations=READ_ONLY, output="x" * 30_000)
    executor, _, _, _ = _executor(policy=policy, caller=caller)

    result = await executor.call_tool(node_id="n", server_id="srv", tool="read_file", arguments={})

    assert "[truncated]" in result
    assert len(result) < 30_000


async def test_audit_log_records_every_call_and_verifies() -> None:
    policy = ToolPolicy(id="p", grants=[_grant()])
    executor, _, _, audit_log = _executor(policy=policy)

    await executor.call_tool(node_id="n", server_id="srv", tool="read_file", arguments={})
    with pytest.raises(ToolBlockedError):
        await executor.call_tool(node_id="n", server_id="srv", tool="other_tool", arguments={})

    assert len(audit_log.records) == 2
    assert audit_log.verify() is True


async def test_tampering_with_a_record_breaks_the_chain() -> None:
    # Tampering the latest record is undetectable by construction (nothing
    # newer anchors its hash) — this checks the property the chain actually
    # gives: altering an earlier record invalidates everything after it.
    policy = ToolPolicy(id="p", grants=[_grant()])
    executor, _, _, audit_log = _executor(policy=policy)
    await executor.call_tool(node_id="n", server_id="srv", tool="read_file", arguments={})
    await executor.call_tool(node_id="n", server_id="srv", tool="read_file", arguments={})
    assert audit_log.verify() is True

    import dataclasses

    tampered = dataclasses.replace(audit_log.records[0], decision="executed (tampered)")
    audit_log._records[0] = tampered  # type: ignore[attr-defined]

    assert audit_log.verify() is False
