import { AgentIcon, ToolIcon } from "../nodes/icons";
import { useFlowStore } from "../store/flowStore";

export function Palette() {
  const addNode = useFlowStore((state) => state.addNode);

  return (
    <aside className="palette">
      <div className="palette__title">Add node</div>
      <button
        type="button"
        className="palette__item palette__item--agent"
        onClick={() => addNode("agent")}
      >
        <AgentIcon />
        <span>Agent</span>
      </button>
      <button
        type="button"
        className="palette__item palette__item--mcp-tool"
        onClick={() => addNode("mcp_tool")}
      >
        <ToolIcon />
        <span>MCP Tool</span>
      </button>
    </aside>
  );
}
