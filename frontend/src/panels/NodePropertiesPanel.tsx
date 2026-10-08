import { useSelectedNode, useFlowStore } from "../store/flowStore";

export function NodePropertiesPanel() {
  const node = useSelectedNode();
  const updateNodeData = useFlowStore((state) => state.updateNodeData);

  if (!node) {
    return <aside className="panel panel--empty">Select a node to edit it.</aside>;
  }

  if (node.type === "agent") {
    const { data } = node;
    return (
      <aside className="panel">
        <h3>Agent</h3>
        <label>
          Label
          <input value={data.label} onChange={(e) => updateNodeData(node.id, { label: e.target.value })} />
        </label>
        <label>
          Model
          <input value={data.model} onChange={(e) => updateNodeData(node.id, { model: e.target.value })} />
        </label>
        <label>
          System Prompt
          <textarea
            value={data.system_prompt}
            onChange={(e) => updateNodeData(node.id, { system_prompt: e.target.value })}
          />
        </label>
        <label>
          Input Template
          <textarea
            value={data.input_template}
            onChange={(e) => updateNodeData(node.id, { input_template: e.target.value })}
          />
        </label>
        <label>
          Temperature
          <input
            type="number"
            min={0}
            max={1}
            step={0.1}
            value={data.temperature ?? 0.2}
            onChange={(e) => updateNodeData(node.id, { temperature: Number(e.target.value) })}
          />
        </label>
        <label>
          Max Tokens
          <input
            type="number"
            min={1}
            value={data.max_tokens ?? 1024}
            onChange={(e) => updateNodeData(node.id, { max_tokens: Number(e.target.value) })}
          />
        </label>
      </aside>
    );
  }

  const { data } = node;
  return (
    <aside className="panel">
      <h3>MCP Tool</h3>
      <label>
        Label
        <input value={data.label} onChange={(e) => updateNodeData(node.id, { label: e.target.value })} />
      </label>
      <label>
        Server ID
        <input value={data.server_id} onChange={(e) => updateNodeData(node.id, { server_id: e.target.value })} />
      </label>
      <label>
        Tool Name
        <input value={data.tool_name} onChange={(e) => updateNodeData(node.id, { tool_name: e.target.value })} />
      </label>
      <label>
        Tool Policy ID
        <input
          value={data.tool_policy_id}
          onChange={(e) => updateNodeData(node.id, { tool_policy_id: e.target.value })}
        />
      </label>
      <ArgumentsEditor
        arguments={data.arguments}
        onChange={(args) => updateNodeData(node.id, { arguments: args })}
      />
    </aside>
  );
}

function ArgumentsEditor({
  arguments: args,
  onChange,
}: {
  arguments: Record<string, string>;
  onChange: (args: Record<string, string>) => void;
}) {
  const entries = Object.entries(args);

  return (
    <div className="arguments-editor">
      <span>Arguments</span>
      {entries.map(([key, value], index) => (
        <div className="arguments-editor__row" key={index}>
          <input
            placeholder="key"
            value={key}
            onChange={(e) => {
              const next = Object.fromEntries(entries);
              delete next[key];
              next[e.target.value] = value;
              onChange(next);
            }}
          />
          <input
            placeholder="value or {{outputs.x.y}}"
            value={value}
            onChange={(e) => {
              const next = { ...args, [key]: e.target.value };
              onChange(next);
            }}
          />
          <button
            type="button"
            onClick={() => {
              const next = { ...args };
              delete next[key];
              onChange(next);
            }}
          >
            ✕
          </button>
        </div>
      ))}
      <button type="button" onClick={() => onChange({ ...args, "": "" })}>
        + argument
      </button>
    </div>
  );
}
