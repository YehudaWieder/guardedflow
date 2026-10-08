import { Handle, Position as HandlePosition, type NodeProps } from "@xyflow/react";

import type { FlowNode } from "../canvas/graphDocument";

type MCPToolNodeProps = NodeProps<Extract<FlowNode, { type: "mcp_tool" }>>;

export function MCPToolNodeView({ data, selected }: MCPToolNodeProps) {
  return (
    <div className={`flow-node flow-node--mcp-tool${selected ? " is-selected" : ""}`}>
      <Handle type="target" position={HandlePosition.Left} />
      <div className="flow-node__kind">MCP Tool</div>
      <div className="flow-node__label">{data.label}</div>
      <div className="flow-node__detail">
        {data.server_id || "…"} / {data.tool_name || "…"}
      </div>
      <Handle type="source" position={HandlePosition.Right} />
    </div>
  );
}
