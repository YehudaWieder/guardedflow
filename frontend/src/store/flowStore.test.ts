import { beforeEach, describe, expect, it } from "vitest";

import { useFlowStore } from "./flowStore";

function resetStore() {
  useFlowStore.setState({
    name: "untitled_flow",
    entry: null,
    nodes: [],
    edges: [],
    selectedNodeId: null,
    nextId: { agent: 1, mcp_tool: 1 },
  });
}

describe("flowStore", () => {
  beforeEach(resetStore);

  it("assigns incrementing ids per node kind and sets the first node as entry", () => {
    const { addNode } = useFlowStore.getState();
    addNode("agent", { x: 0, y: 0 });
    addNode("agent", { x: 0, y: 100 });
    addNode("mcp_tool", { x: 200, y: 0 });

    const { nodes, entry } = useFlowStore.getState();
    expect(nodes.map((n) => n.id)).toEqual(["agent_1", "agent_2", "mcp_tool_1"]);
    expect(entry).toBe("agent_1");
  });

  it("updates only the targeted node's data", () => {
    const { addNode, updateNodeData } = useFlowStore.getState();
    addNode("agent", { x: 0, y: 0 });
    addNode("agent", { x: 0, y: 100 });

    updateNodeData("agent_2", { label: "Renamed" });

    const { nodes } = useFlowStore.getState();
    expect(nodes.find((n) => n.id === "agent_1")?.data.label).toBe("Agent");
    expect(nodes.find((n) => n.id === "agent_2")?.data.label).toBe("Renamed");
  });

  it("does not overwrite an explicitly chosen entry when more nodes are added", () => {
    const { addNode, setEntry } = useFlowStore.getState();
    addNode("agent", { x: 0, y: 0 });
    setEntry("agent_1");
    addNode("mcp_tool", { x: 200, y: 0 });

    expect(useFlowStore.getState().entry).toBe("agent_1");
  });
});
