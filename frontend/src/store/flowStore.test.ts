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
    connectionError: null,
  });
}

describe("flowStore", () => {
  beforeEach(resetStore);

  it("assigns incrementing ids and distinct default labels per node kind", () => {
    const { addNode } = useFlowStore.getState();
    addNode("agent");
    addNode("agent");
    addNode("mcp_tool");

    const { nodes, entry } = useFlowStore.getState();
    expect(nodes.map((n) => n.id)).toEqual(["agent_1", "agent_2", "mcp_tool_1"]);
    expect(nodes.map((n) => n.data.label)).toEqual(["Agent 1", "Agent 2", "MCP Tool 1"]);
    expect(entry).toBe("agent_1");
  });

  it("never places two nodes at the same position", () => {
    const { addNode } = useFlowStore.getState();
    addNode("agent");
    addNode("agent");
    addNode("mcp_tool");

    const { nodes } = useFlowStore.getState();
    const positions = nodes.map((n) => `${n.position.x},${n.position.y}`);
    expect(new Set(positions).size).toBe(positions.length);
  });

  it("updates only the targeted node's data", () => {
    const { addNode, updateNodeData } = useFlowStore.getState();
    addNode("agent");
    addNode("agent");

    updateNodeData("agent_2", { label: "Renamed" });

    const { nodes } = useFlowStore.getState();
    expect(nodes.find((n) => n.id === "agent_1")?.data.label).toBe("Agent 1");
    expect(nodes.find((n) => n.id === "agent_2")?.data.label).toBe("Renamed");
  });

  it("does not overwrite an explicitly chosen entry when more nodes are added", () => {
    const { addNode, setEntry } = useFlowStore.getState();
    addNode("agent");
    setEntry("agent_1");
    addNode("mcp_tool");

    expect(useFlowStore.getState().entry).toBe("agent_1");
  });

  it("removes a node along with its connected edges", () => {
    const { addNode, onConnect } = useFlowStore.getState();
    addNode("agent");
    addNode("mcp_tool");
    onConnect({ source: "agent_1", target: "mcp_tool_1", sourceHandle: null, targetHandle: null });

    useFlowStore.getState().removeNode("mcp_tool_1");

    const { nodes, edges } = useFlowStore.getState();
    expect(nodes.map((n) => n.id)).toEqual(["agent_1"]);
    expect(edges).toEqual([]);
  });

  it("reassigns entry to a remaining node when the entry node is removed", () => {
    const { addNode } = useFlowStore.getState();
    addNode("agent");
    addNode("agent");

    useFlowStore.getState().removeNode("agent_1");

    expect(useFlowStore.getState().entry).toBe("agent_2");
  });

  it("clears entry when the last node is removed", () => {
    const { addNode } = useFlowStore.getState();
    addNode("agent");

    useFlowStore.getState().removeNode("agent_1");

    expect(useFlowStore.getState().entry).toBeNull();
  });

  it("rejects a connection that would create a cycle", () => {
    const { addNode, onConnect } = useFlowStore.getState();
    addNode("agent");
    addNode("agent");
    onConnect({ source: "agent_1", target: "agent_2", sourceHandle: null, targetHandle: null });

    onConnect({ source: "agent_2", target: "agent_1", sourceHandle: null, targetHandle: null });

    const { edges, connectionError } = useFlowStore.getState();
    expect(edges).toHaveLength(1);
    expect(connectionError).not.toBeNull();
  });
});
