import { Handle, Position as HandlePosition, type NodeProps } from "@xyflow/react";

import type { FlowNode } from "../canvas/graphDocument";
import { ToolIcon } from "./icons";

type MCPToolNodeProps = NodeProps<Extract<FlowNode, { type: "mcp_tool" }>>;

// Low and wide, unlike the agent's tall card — a tool is a small utility
// docked beside the agent, not something that competes with it for space.
export function MCPToolNodeView({ data, selected }: MCPToolNodeProps) {
  return (
    <div className={`flow-node flow-node--mcp-tool${selected ? " is-selected" : ""}`}>
      <Handle type="target" position={HandlePosition.Left} />
      <div className="flow-node__badge">
        <ToolIcon />
      </div>
      <div className="flow-node__body">
        <div className="flow-node__label">{data.label}</div>
        <div className="flow-node__server">
          {data.server_id || "…"} · {data.tool_name || "…"}
        </div>
      </div>
      <Handle type="source" position={HandlePosition.Right} />
    </div>
  );
}
