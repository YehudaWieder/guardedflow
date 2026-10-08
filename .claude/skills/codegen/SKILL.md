---
name: codegen
description: Rules for the IR and the generator that turns flows into LangGraph Python — NodeEmitters, Jinja2 templates, flow_config.json, the exported project template, and snapshot/equivalence tests. Use whenever adding a node type, changing generated output, or touching backend/app/core/ir or backend/app/codegen.
---

# IR and code generation

The platform runs the module this generator produces, and the user downloads the same module. Generated code is both the runtime and the product, so it must be correct and read like a careful person wrote it.

## Invariants
1. User strings (prompts, templates, labels, argument values) never appear in generated Python. They go to `flow_config.json` and are loaded at runtime. Generated code holds only structure: names, edges, conditions.
2. Node ids are schema-validated identifiers — the only user input that becomes a Python name.
3. Same IR → byte-identical output. Sort anything that comes from a dict or set.
4. Every generated file passes `ast.parse`, `ruff check`, `ruff format --check`, `mypy --strict`.

## Adding a node type
1. Model in `core/schemas` (a new member of the discriminated union).
2. Normalization in `core/ir`: resolve references, check upstream dependencies.
3. One `NodeEmitter` and one template, registered. Nothing else in the generator should change — if it must, the emitter interface is missing something; fix the interface.
4. A fixture flow in `examples/flows/` that uses it; snapshot and equivalence tests pick it up automatically.

## What generated code looks like
- Plain functions and explicit edges. No metaprogramming, no generic dispatch-by-type.
- Only used imports. No comments except the header line with flow name and version hash.
- Shared helpers live in `flowpermit` or the vendored runtime module, not repeated per node.

## Snapshots
A snapshot diff is a code review of generated output. Read it; never bulk-update snapshots to make tests pass.
