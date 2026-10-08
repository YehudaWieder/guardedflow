# GuardedFlow

Visual builder for LangGraph agent flows. One IR feeds both in-platform runs and code export; every MCP tool call goes through `flowpermit`. `docs/PLAN.md` is the source of truth for architectural decisions: read the relevant section before starting a phase, and don't re-decide them in code. The plan predates the rename — `agentguard` there means `flowpermit`.

## Layout
- `docs/PLAN.md` — the project plan
- `backend/app/api` — FastAPI routes (thin)
- `backend/app/core/schemas` — GraphDocument, ToolPolicy, events (Pydantic v2); source of truth for all types
- `backend/app/core/ir` — validation and normalization to IR
- `backend/app/codegen` — NodeEmitters + Jinja2 templates
- `backend/app/runs` — Run Manager, event store, SSE
- `backend/app/mcp_adapter` — the only place that touches the MCP SDK
- `backend/flowpermit` — standalone package, vendored into every export
- `frontend/src/generated` — TS types generated from JSON Schema; never edit by hand
- `examples/flows` — fixture flows for tests and the demo

## Commands
- Backend: `uv run pytest` · `uv run ruff check .` · `uv run mypy --strict app flowpermit`
- Frontend: `pnpm test` · `pnpm typecheck` · `pnpm gen:types`

Run the checks for the area you touched before saying a change is done.

## How we write code
The goal is the smallest correct change, written the way a senior engineer would leave it.

- **Fix causes, not symptoms.** If a bug comes from a wrong model, signature, or invariant, change it there and update the callers. Don't add a special case, flag, or fallback downstream to route around it.
- **Trust the types.** Data is validated once, at the boundary (API input, MCP output, file load). Inside, don't re-check what the type guarantees: no `is None` checks on non-optional values, no `isinstance` on typed parameters, no `try` around code that can't raise what you catch.
- **Let errors surface.** No broad `except`, no `except: pass`, no `.get(key, "")` that turns a missing key into a silent empty value. Catch only what you can handle, where you can handle it.
- **Pass what's needed, nothing more.** No unused parameters, no threading a value through layers that ignore it, no passing both an object and one of its fields.
- **No speculative structure.** No interface with a single implementation unless the plan names it a port (`ChatModelPort`, `ApprovalHandler`). No "for later" parameters, unused config options, or compatibility shims — this is a greenfield project.
- **Names over comments.** Comment only the *why* the code can't express. No step-narrating comments, no docstrings that restate the signature.
- **Keep diffs scoped.** Don't reformat, rename, or improve code outside the task; mention what you noticed instead.
- **New dependencies** only when they remove real complexity — ask first.

When two designs both work, choose the one with less code and fewer concepts, and state why in one sentence.

## Skills
Load the matching skill before working in an area: `python-backend`, `react-frontend`, `codegen`, `flowpermit`, `testing`. Run `review-diff` before finishing any change.
