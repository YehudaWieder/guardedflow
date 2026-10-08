import type { Edge as RFEdge, Node as RFNode } from "@xyflow/react";

import type {
  AgentNode,
  Edge as DomainEdge,
  GraphDocument,
  MCPToolNode,
  ToolPolicy,
} from "../generated/GraphDocument";

export type AgentNodeData = Omit<AgentNode, "id" | "position" | "type">;
export type MCPToolNodeData = Omit<MCPToolNode, "id" | "position" | "type">;

export type FlowNode = RFNode<AgentNodeData, "agent"> | RFNode<MCPToolNodeData, "mcp_tool">;
export type FlowEdge = RFEdge;

export interface FlowMeta {
  name: string;
  entry: string;
  policies: ToolPolicy[];
}

/** Canvas state only supports agent/mcp_tool nodes in Phase 1; router/validator land in Phase 5. */
export class UnsupportedNodeTypeError extends Error {
  constructor(type: string) {
    super(`Canvas does not support node type "${type}" yet`);
  }
}

export function toGraphDocument(meta: FlowMeta, nodes: FlowNode[], edges: FlowEdge[]): GraphDocument {
  return {
    schema_version: 1,
    name: meta.name,
    entry: meta.entry,
    policies: meta.policies,
    nodes: nodes.map(nodeToDomain),
    edges: edges.map(edgeToDomain),
  };
}

export function fromGraphDocument(doc: GraphDocument): {
  meta: FlowMeta;
  nodes: FlowNode[];
  edges: FlowEdge[];
} {
  return {
    meta: { name: doc.name, entry: doc.entry, policies: doc.policies ?? [] },
    nodes: doc.nodes.map(nodeFromDomain),
    edges: doc.edges.map((edge) => ({ id: edge.id, source: edge.source, target: edge.target })),
  };
}

function nodeToDomain(node: FlowNode): AgentNode | MCPToolNode {
  if (node.type === "agent") {
    return { id: node.id, position: node.position, type: "agent", ...node.data };
  }
  return { id: node.id, position: node.position, type: "mcp_tool", ...node.data };
}

function edgeToDomain(edge: FlowEdge): DomainEdge {
  return { id: edge.id, source: edge.source, target: edge.target };
}

function nodeFromDomain(node: AgentNode | MCPToolNode | { type?: string }): FlowNode {
  if (node.type === "agent") {
    const { id, position, type: _type, ...data } = node as AgentNode;
    return { id, position, type: "agent", data };
  }
  if (node.type === "mcp_tool") {
    const { id, position, type: _type, ...data } = node as MCPToolNode;
    return { id, position, type: "mcp_tool", data };
  }
  throw new UnsupportedNodeTypeError(node.type ?? "unknown");
}
