import { describe, expect, it } from "vitest";

import { wouldCreateCycle } from "./cycles";

describe("wouldCreateCycle", () => {
  it("allows a connection that extends a chain", () => {
    const edges = [{ source: "a", target: "b" }];
    expect(wouldCreateCycle(edges, { source: "b", target: "c" })).toBe(false);
  });

  it("rejects a self-loop", () => {
    expect(wouldCreateCycle([], { source: "a", target: "a" })).toBe(true);
  });

  it("rejects a direct two-node cycle", () => {
    const edges = [{ source: "a", target: "b" }];
    expect(wouldCreateCycle(edges, { source: "b", target: "a" })).toBe(true);
  });

  it("rejects a cycle closed through an intermediate node", () => {
    const edges = [
      { source: "a", target: "b" },
      { source: "b", target: "c" },
    ];
    expect(wouldCreateCycle(edges, { source: "c", target: "a" })).toBe(true);
  });

  it("allows branching that does not loop back", () => {
    const edges = [{ source: "a", target: "b" }];
    expect(wouldCreateCycle(edges, { source: "a", target: "c" })).toBe(false);
  });
});
