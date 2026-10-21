import { type ReactNode, useState } from "react";

import type { AgentNodeData, MCPToolNodeData } from "../canvas/graphDocument";
import { AgentFace, ToolIcon } from "../nodes/icons";
import { useFlowStore, useSelectedNode } from "../store/flowStore";

export function NodePropertiesPanel() {
  const node = useSelectedNode();
  const updateNodeData = useFlowStore((state) => state.updateNodeData);
  const removeNode = useFlowStore((state) => state.removeNode);

  if (!node) {
    return (
      <aside className="panel panel--empty">
        <p>Select a node to edit it.</p>
      </aside>
    );
  }

  const isAgent = node.type === "agent";
  return (
    <aside className={`panel panel--${isAgent ? "agent" : "mcp-tool"}`}>
      <header className="panel__header">
        <div className={`panel__icon panel__icon--${isAgent ? "agent" : "mcp-tool"}`}>
          {isAgent ? <AgentFace /> : <ToolIcon />}
        </div>
        <div>
          <div className="panel__kind">{isAgent ? "Agent" : "MCP Tool"}</div>
          <div className="panel__id">{node.id}</div>
        </div>
        <button
          type="button"
          className="panel__delete"
          onClick={() => removeNode(node.id)}
          title="Delete node"
          aria-label="Delete node"
        >
          Delete
        </button>
      </header>

      {isAgent ? (
        <AgentFields
          key={node.id}
          data={node.data}
          onChange={(patch) => updateNodeData(node.id, patch)}
        />
      ) : (
        <MCPToolFields
          key={node.id}
          data={node.data}
          onChange={(patch) => updateNodeData(node.id, patch)}
        />
      )}
    </aside>
  );
}

function AgentFields({
  data,
  onChange,
}: {
  data: AgentNodeData;
  onChange: (patch: Partial<AgentNodeData>) => void;
}) {
  return (
    <>
      <Section title="Identity">
        <Field label="Label">
          <input value={data.label} onChange={(e) => onChange({ label: e.target.value })} />
        </Field>
      </Section>

      <Section title="Model">
        <Field label="Model">
          <input
            value={data.model}
            placeholder="claude-sonnet-5"
            onChange={(e) => onChange({ model: e.target.value })}
          />
        </Field>
        <div className="field-row">
          <Field label="Temperature">
            <div className="slider-field">
              <input
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={data.temperature ?? 0.2}
                onChange={(e) => onChange({ temperature: Number(e.target.value) })}
              />
              <input
                type="number"
                min={0}
                max={1}
                step={0.05}
                className="slider-field__number"
                value={data.temperature ?? 0.2}
                onChange={(e) => onChange({ temperature: Number(e.target.value) })}
              />
            </div>
          </Field>
          <Field label="Max Tokens">
            <input
              type="number"
              min={1}
              value={data.max_tokens ?? 1024}
              onChange={(e) => onChange({ max_tokens: Number(e.target.value) })}
            />
          </Field>
        </div>
      </Section>

      <Section title="Prompt">
        <Field label="System Prompt">
          <textarea
            className="mono"
            value={data.system_prompt}
            onChange={(e) => onChange({ system_prompt: e.target.value })}
          />
        </Field>
        <Field label="Input Template" hint="e.g. {{outputs.other_node.text}}">
          <textarea
            className="mono"
            value={data.input_template}
            onChange={(e) => onChange({ input_template: e.target.value })}
          />
        </Field>
      </Section>

      <Section title="Tool access">
        <Field label="Tool Policy ID" hint="Leave empty if this agent calls no tools">
          <input
            value={data.tool_policy_id ?? ""}
            onChange={(e) => onChange({ tool_policy_id: e.target.value === "" ? null : e.target.value })}
          />
        </Field>
      </Section>

      <Section title="Structured output">
        <JSONField
          label="Output Schema"
          hint="JSON Schema for this agent's output, or leave empty"
          value={data.output_schema ?? null}
          onChange={(value) => onChange({ output_schema: value })}
        />
      </Section>
    </>
  );
}

function MCPToolFields({
  data,
  onChange,
}: {
  data: MCPToolNodeData;
  onChange: (patch: Partial<MCPToolNodeData>) => void;
}) {
  return (
    <>
      <Section title="Identity">
        <Field label="Label">
          <input value={data.label} onChange={(e) => onChange({ label: e.target.value })} />
        </Field>
      </Section>

      <Section title="Connection">
        <div className="field-row">
          <Field label="Server ID">
            <input value={data.server_id} onChange={(e) => onChange({ server_id: e.target.value })} />
          </Field>
          <Field label="Tool Name">
            <input value={data.tool_name} onChange={(e) => onChange({ tool_name: e.target.value })} />
          </Field>
        </div>
        <Field label="Tool Policy ID">
          <input
            value={data.tool_policy_id}
            onChange={(e) => onChange({ tool_policy_id: e.target.value })}
          />
        </Field>
      </Section>

      <Section title="Arguments">
        <ArgumentsEditor
          arguments={data.arguments}
          onChange={(args) => onChange({ arguments: args })}
        />
      </Section>
    </>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="panel__section">
      <h4 className="panel__section-title">{title}</h4>
      {children}
    </section>
  );
}

function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return (
    <label className="field">
      <span className="field__label">{label}</span>
      {children}
      {hint ? <span className="field__hint">{hint}</span> : null}
    </label>
  );
}

function JSONField({
  label,
  hint,
  value,
  onChange,
}: {
  label: string;
  hint?: string;
  value: Record<string, unknown> | null;
  onChange: (value: Record<string, unknown> | null) => void;
}) {
  const [text, setText] = useState(() => (value ? JSON.stringify(value, null, 2) : ""));
  const [error, setError] = useState<string | null>(null);

  return (
    <Field label={label} hint={hint}>
      <textarea
        className="mono"
        value={text}
        placeholder="{}"
        onChange={(e) => {
          const next = e.target.value;
          setText(next);
          if (next.trim() === "") {
            setError(null);
            onChange(null);
            return;
          }
          try {
            const parsed = JSON.parse(next);
            setError(null);
            onChange(parsed);
          } catch {
            setError("Invalid JSON");
          }
        }}
      />
      {error ? <span className="field__error">{error}</span> : null}
    </Field>
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
            className="arguments-editor__remove"
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
      <button type="button" className="arguments-editor__add" onClick={() => onChange({ ...args, "": "" })}>
        + argument
      </button>
    </div>
  );
}
