import type { NodeTypes } from "@xyflow/react";

import { AgentNodeView } from "./AgentNodeView";
import { MCPToolNodeView } from "./MCPToolNodeView";

// Defined once at module level: a fresh object here would re-mount every node on each render.
export const nodeTypes: NodeTypes = {
  agent: AgentNodeView,
  mcp_tool: MCPToolNodeView,
};
