import { Handle, Position as HandlePosition, type NodeProps } from "@xyflow/react";

import type { FlowNode } from "../canvas/graphDocument";
import { AgentFace } from "./icons";

type AgentNodeProps = NodeProps<Extract<FlowNode, { type: "agent" }>>;

// Agent is the one node shaped like a character: a round head above a
// rectangular body (where its info lives), with the in/out handles styled
// as hands reaching out from the body's sides.
export function AgentNodeView({ data, selected }: AgentNodeProps) {
  return (
    <div className={`flow-node flow-node--agent${selected ? " is-selected" : ""}`}>
      <div className="flow-node--agent__head">
        <AgentFace />
      </div>
      <Handle type="target" position={HandlePosition.Left} />
      <div className="flow-node__body">
        <div className="flow-node__kind">Agent</div>
        <div className="flow-node__label">{data.label}</div>
        <div className="flow-node__detail">{data.model}</div>
      </div>
      <Handle type="source" position={HandlePosition.Right} />
    </div>
  );
}
