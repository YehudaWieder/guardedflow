import { Handle, Position as HandlePosition, type NodeProps } from "@xyflow/react";

import type { FlowNode } from "../canvas/graphDocument";

type AgentNodeProps = NodeProps<Extract<FlowNode, { type: "agent" }>>;

export function AgentNodeView({ data, selected }: AgentNodeProps) {
  return (
    <div className={`flow-node flow-node--agent${selected ? " is-selected" : ""}`}>
      <Handle type="target" position={HandlePosition.Left} />
      <div className="flow-node__kind">Agent</div>
      <div className="flow-node__label">{data.label}</div>
      <div className="flow-node__detail">{data.model}</div>
      <Handle type="source" position={HandlePosition.Right} />
    </div>
  );
}
