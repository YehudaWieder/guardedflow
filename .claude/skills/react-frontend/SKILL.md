---
name: react-frontend
description: Conventions for this repo's React / TypeScript / React Flow / Zustand frontend. Use for any work under frontend/ — canvas, custom nodes, store, SSE handling, trace / approval / audit panels, and component refactors.
---

# React frontend

React, TypeScript strict, Vite, `@xyflow/react`, Zustand.

## Types
- Domain types come from `src/generated/`. Never redeclare them; if one is wrong, fix the Pydantic model and regenerate.
- No `any`. An `as` cast needs a one-line reason.

## State
- The store holds what can't be derived: the GraphDocument, run events, pending approvals. Split into slices by concern; components select the narrowest slice they need.
- Derived values (node run status, counts, selected node details) are selectors, not stored copies.
- A `useEffect` that syncs one piece of state into another means the state lives in the wrong place.

## Canvas
- One component per node type in `src/nodes/`, registered in a `nodeTypes` map defined at module level (a new object identity re-mounts every node).
- Canvas ↔ GraphDocument conversion is one pure, tested module. Positions are UI-only.

## Server communication
- One API client module and one SSE hook. The hook resumes from the last `seq` and appends events to the store; panels derive their views from events.
- No optimistic updates for runs or approvals — the server event is the truth.

## Components
- Props are the data a component renders plus callbacks — not the whole store, not an id to look up an object the parent already has.
- No components that only forward props, no custom hooks that wrap a single library call.
