import type { Connection, EdgeChange, NodeChange, XYPosition } from "@xyflow/react";
import { addEdge, applyEdgeChanges, applyNodeChanges } from "@xyflow/react";
import { create } from "zustand";

import { wouldCreateCycle } from "../canvas/cycles";
import type { AgentNodeData, FlowEdge, FlowNode, MCPToolNodeData } from "../canvas/graphDocument";

type NodeKind = "agent" | "mcp_tool";

// New nodes cascade diagonally in a wrapping grid so they never land exactly
// on top of an existing one.
const GRID_STEP = 180;
const GRID_COLUMNS = 4;
const GRID_ORIGIN: XYPosition = { x: 100, y: 80 };

function cascadePosition(index: number): XYPosition {
  return {
    x: GRID_ORIGIN.x + (index % GRID_COLUMNS) * GRID_STEP,
    y: GRID_ORIGIN.y + Math.floor(index / GRID_COLUMNS) * GRID_STEP,
  };
}

const DEFAULT_AGENT_DATA: Omit<AgentNodeData, "label"> = {
  model: "gpt-4o-mini",
  system_prompt: "",
  input_template: "",
  temperature: 0.2,
  max_tokens: 1024,
};

const DEFAULT_MCP_TOOL_DATA: Omit<MCPToolNodeData, "label"> = {
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
  connectionError: string | null;

  setName: (name: string) => void;
  setEntry: (id: string) => void;
  addNode: (kind: NodeKind) => void;
  removeNode: (id: string) => void;
  updateNodeData: (id: string, patch: Partial<AgentNodeData> | Partial<MCPToolNodeData>) => void;
  selectNode: (id: string | null) => void;
  onNodesChange: (changes: NodeChange<FlowNode>[]) => void;
  onEdgesChange: (changes: EdgeChange<FlowEdge>[]) => void;
  onConnect: (connection: Connection) => void;
  clearConnectionError: () => void;
}

export const useFlowStore = create<FlowState>((set, get) => ({
  name: "untitled_flow",
  entry: null,
  nodes: [],
  edges: [],
  selectedNodeId: null,
  nextId: { agent: 1, mcp_tool: 1 },
  connectionError: null,

  setName: (name) => set({ name }),
  setEntry: (id) => set({ entry: id }),

  addNode: (kind) => {
    const n = get().nextId[kind];
    const id = `${kind}_${n}`;
    const position = cascadePosition(get().nodes.length);
    const node: FlowNode =
      kind === "agent"
        ? { id, type: "agent", position, data: { ...DEFAULT_AGENT_DATA, label: `Agent ${n}` } }
        : { id, type: "mcp_tool", position, data: { ...DEFAULT_MCP_TOOL_DATA, label: `MCP Tool ${n}` } };
    set((state) => ({
      nodes: [...state.nodes, node],
      entry: state.entry ?? id,
      nextId: { ...state.nextId, [kind]: n + 1 },
    }));
  },

  removeNode: (id) => {
    set((state) => {
      const nodes = state.nodes.filter((node) => node.id !== id);
      const edges = state.edges.filter((edge) => edge.source !== id && edge.target !== id);
      return {
        nodes,
        edges,
        entry: state.entry === id ? (nodes[0]?.id ?? null) : state.entry,
        selectedNodeId: state.selectedNodeId === id ? null : state.selectedNodeId,
      };
    });
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

  onConnect: (connection) => {
    set((state) => {
      if (wouldCreateCycle(state.edges, connection)) {
        return {
          connectionError:
            "That connection would create a cycle — only Router/Validator loops are allowed, and neither is on the canvas yet.",
        };
      }
      return { edges: addEdge(connection, state.edges), connectionError: null };
    });
  },

  clearConnectionError: () => set({ connectionError: null }),
}));

export function useSelectedNode(): FlowNode | null {
  return useFlowStore((state) => state.nodes.find((node) => node.id === state.selectedNodeId) ?? null);
}
