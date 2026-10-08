---
name: python-backend
description: Conventions for this repo's FastAPI / Pydantic v2 / SQLAlchemy / LangGraph backend. Use for any work under backend/ — routes, schemas, IR, Run Manager, SSE, persistence, MCP adapter — including new endpoints, refactors, and bug fixes.
---

# Python backend

Python 3.12, Pydantic v2, FastAPI, SQLAlchemy 2.0 async, LangGraph, the `mcp` SDK. `mypy --strict` must pass.

## Shape of the code
- Modules hold functions. Use a class only when it owns state or a resource lifecycle (a session, a run). A class with `__init__` and one method is a function.
- Routes are thin: parse, call one function in `core` or `runs`, return. No business logic or queries in route bodies.
- One `Settings` object (pydantic-settings), built in the app factory and injected. Nothing else reads `os.environ`.
- No module-level mutable state. Long-lived resources (DB engine, MCP sessions) are created in the lifespan handler.

## Types and validation
- Pydantic at boundaries: HTTP, files, MCP responses, LLM structured output. Inside, pass the validated models; don't convert back and forth.
- Prefer `Literal` and discriminated unions over free strings and boolean flags.
- `dict[str, Any]` crossing a module boundary means a model is missing.

## Errors
- Domain errors are small classes in `core/errors.py`, mapped to HTTP responses in exactly one exception handler.
- Unexpected exceptions propagate; the Run Manager records them as a failed run. Don't wrap-and-reraise without adding information.

## Async
- Everything on the request and run path is async. Blocking work goes through `asyncio.to_thread`.
- A run is a task owned by the Run Manager, never by the HTTP request. Cancellation is `task.cancel()`, handled in one place.

## Boundaries
- Only `app/mcp_adapter` imports `mcp`.
- Every tool call goes through `flowpermit` — no second path, including in tests.
