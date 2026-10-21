import { Background, Controls, MarkerType, Panel, ReactFlow } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useEffect } from "react";

import { nodeTypes } from "../nodes/nodeTypes";
import { useFlowStore } from "../store/flowStore";

const DEFAULT_EDGE_OPTIONS = {
  markerEnd: { type: MarkerType.ArrowClosed },
};

export function Canvas() {
  const nodes = useFlowStore((state) => state.nodes);
  const edges = useFlowStore((state) => state.edges);
  const onNodesChange = useFlowStore((state) => state.onNodesChange);
  const onEdgesChange = useFlowStore((state) => state.onEdgesChange);
  const onConnect = useFlowStore((state) => state.onConnect);
  const selectNode = useFlowStore((state) => state.selectNode);
  const connectionError = useFlowStore((state) => state.connectionError);
  const clearConnectionError = useFlowStore((state) => state.clearConnectionError);

  useEffect(() => {
    if (!connectionError) return;
    const timeout = setTimeout(clearConnectionError, 4000);
    return () => clearTimeout(timeout);
  }, [connectionError, clearConnectionError]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      defaultEdgeOptions={DEFAULT_EDGE_OPTIONS}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      onNodeClick={(_, node) => selectNode(node.id)}
      onPaneClick={() => selectNode(null)}
      fitView
    >
      <Background />
      <Controls />
      {connectionError ? (
        <Panel position="top-center" className="canvas__toast">
          {connectionError}
        </Panel>
      ) : null}
    </ReactFlow>
  );
}
