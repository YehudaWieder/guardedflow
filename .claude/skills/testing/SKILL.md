---
name: testing
description: How to write tests in this repo — pytest / pytest-asyncio, hypothesis, syrupy snapshots, the scripted fake model, the FastMCP test server, equivalence tests, Vitest, and Playwright. Use whenever writing, fixing, or reviewing tests, or when a change needs coverage.
---

# Testing

Tests exist to catch behavior regressions. Fewer, sharper tests beat many shallow ones.

## Write
- Test through public interfaces: a route, a module's API, the generated graph — not private helpers.
- Fakes over mocks: the scripted model (`tests/fakes/model.py`) and the FastMCP test server. Use a mock only when the call itself is the behavior (e.g. "the tool was never called").
- Use `pytest.mark.parametrize` when cases differ only in data.
- Name tests by behavior: `test_tool_with_changed_schema_is_blocked`.
- A bug fix starts with a failing test that reproduces the bug.

## Don't write
- Tests of Pydantic, FastAPI, or LangGraph themselves.
- Tests that mirror the implementation, or assert on log output.
- Tests added only for coverage numbers.
- Sleeps — await the event or use a deterministic clock.

## Required layers
- Snapshot tests for each fixture flow's generated code.
- Equivalence: each fixture runs in-platform and as an exported project with the scripted model; normalized traces must match.
- The flowpermit attack suite.
- Four Playwright flows only: build and run, branching, approval, export.
