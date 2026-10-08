---
name: flowpermit
description: Rules for the flowpermit package — tool-call policy enforcement, schema pinning, argument rules, budgets, risk classification, human approval via LangGraph interrupt, and the hash-chained audit log. Use for any change under backend/flowpermit or anything affecting how MCP tools are exposed to or called by agents.
---

# flowpermit

The security boundary, vendored into every exported project. People will audit it: keep it small (under 600 lines), light on dependencies (stdlib, pydantic, jsonschema), and obvious.

## Non-negotiables
- Default deny. No grant means blocked. Unknown risk means risky.
- Fixed check order: grant → schema pin → arguments → budget → risk/approval → execute → audit. No skipping for "trusted" cases; there are none.
- Every decision, including blocks and errors, is audited. Make this true by construction (a single exit path), not by remembering.
- MCP tool annotations are server hints: they can raise risk, never lower it.
- Tool output is untrusted data — size-limited, delimited when passed to the model, never placed in system instructions.
- Secrets are redacted before anything is logged, traced, or audited.

## Design
- `GuardedToolExecutor` is the only thing that calls an MCP tool. Each check is a small pure function from context to decision, testable on its own.
- Approval goes through the `ApprovalHandler` port: `interrupt()` in the platform, a terminal prompt in exports. Edited arguments re-run the argument and budget checks.
- Each audit record includes the SHA-256 of the previous one; `verify` recomputes the chain.

## Tests
Every check has a case in the parametrized attack suite. A change to a check updates its case in the same commit.
