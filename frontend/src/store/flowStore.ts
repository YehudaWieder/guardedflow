import type { Connection, EdgeChange, NodeChange, XYPosition } from "@xyflow/react";
import { addEdge, applyEdgeChanges, applyNodeChanges } from "@xyflow/react";
import { create } from "zustand";

import type { AgentNodeData, FlowEdge, FlowNode, MCPToolNodeData } from "../canvas/graphDocument";

type NodeKind = "agent" | "mcp_tool";

const DEFAULT_AGENT_DATA: AgentNodeData = {
  label: "Agent",
  model: "gpt-4o-mini",
  system_prompt: "",
  input_template: "",
  temperature: 0.2,
  max_tokens: 1024,
};

const DEFAULT_MCP_TOOL_DATA: MCPToolNodeData = {
  label: "MCP Tool",
  server_id: "",
  tool_name: "",
  arguments: {},
  tool_policy_id: "",
};

interface FlowState {
  name: string;
  entry: string | null;
  nodes: FlowNode[];
  edges: FlowEdge[];
  selectedNodeId: string | null;
  nextId: Record<NodeKind, number>;

  setName: (name: string) => void;
  setEntry: (id: string) => void;
  addNode: (kind: NodeKind, position: XYPosition) => void;
  updateNodeData: (id: string, patch: Partial<AgentNodeData & MCPToolNodeData>) => void;
  selectNode: (id: string | null) => void;
  onNodesChange: (changes: NodeChange<FlowNode>[]) => void;
  onEdgesChange: (changes: EdgeChange<FlowEdge>[]) => void;
  onConnect: (connection: Connection) => void;
}

export const useFlowStore = create<FlowState>((set, get) => ({
  name: "untitled_flow",
  entry: null,
  nodes: [],
  edges: [],
  selectedNodeId: null,
  nextId: { agent: 1, mcp_tool: 1 },

  setName: (name) => set({ name }),
  setEntry: (id) => set({ entry: id }),

  addNode: (kind, position) => {
    const n = get().nextId[kind];
    const id = `${kind}_${n}`;
    const node: FlowNode =
      kind === "agent"
        ? { id, type: "agent", position, data: { ...DEFAULT_AGENT_DATA } }
        : { id, type: "mcp_tool", position, data: { ...DEFAULT_MCP_TOOL_DATA } };
    set((state) => ({
      nodes: [...state.nodes, node],
      entry: state.entry ?? id,
      nextId: { ...state.nextId, [kind]: n + 1 },
    }));
  },

  updateNodeData: (id, patch) => {
    set((state) => ({
      nodes: state.nodes.map((node) =>
        node.id === id ? ({ ...node, data: { ...node.data, ...patch } } as FlowNode) : node,
      ),
    }));
  },

  selectNode: (id) => set({ selectedNodeId: id }),

  onNodesChange: (changes) => set((state) => ({ nodes: applyNodeChanges(changes, state.nodes) })),
  onEdgesChange: (changes) => set((state) => ({ edges: applyEdgeChanges(changes, state.edges) })),
  onConnect: (connection) => set((state) => ({ edges: addEdge(connection, state.edges) })),
}));

export function useSelectedNode(): FlowNode | null {
  return useFlowStore((state) => state.nodes.find((node) => node.id === state.selectedNodeId) ?? null);
}
