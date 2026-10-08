import { useFlowStore } from "../store/flowStore";

export function Palette() {
  const addNode = useFlowStore((state) => state.addNode);

  return (
    <aside className="palette">
      <button type="button" onClick={() => addNode("agent", { x: 80, y: 80 })}>
        + Agent
      </button>
      <button type="button" onClick={() => addNode("mcp_tool", { x: 80, y: 220 })}>
        + MCP Tool
      </button>
    </aside>
  );
}
