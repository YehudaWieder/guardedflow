// A cycle among plain agent/mcp_tool edges has no termination condition —
// only Router/Validator loops are allowed (docs/PLAN.md), and neither is
// wired into the canvas yet. This checks before an edge is added, not
// after, so the canvas never holds a connection the IR would reject.

interface EdgeLike {
  source: string;
  target: string;
}

export function wouldCreateCycle(edges: EdgeLike[], candidate: EdgeLike): boolean {
  if (candidate.source === candidate.target) return true;

  const successors = new Map<string, string[]>();
  for (const edge of edges) {
    const list = successors.get(edge.source) ?? [];
    list.push(edge.target);
    successors.set(edge.source, list);
  }

  // A path already exists back to candidate.source means the new edge
  // would close a loop.
  const visited = new Set<string>();
  const stack = [candidate.target];
  while (stack.length > 0) {
    const current = stack.pop() as string;
    if (current === candidate.source) return true;
    if (visited.has(current)) continue;
    visited.add(current);
    for (const next of successors.get(current) ?? []) stack.push(next);
  }

  return false;
}
