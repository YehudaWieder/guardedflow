import { useFlowStore } from "../store/flowStore";

export function Toolbar() {
  const name = useFlowStore((state) => state.name);
  const setName = useFlowStore((state) => state.setName);
  const entry = useFlowStore((state) => state.entry);
  const setEntry = useFlowStore((state) => state.setEntry);
  const nodes = useFlowStore((state) => state.nodes);

  return (
    <header className="toolbar">
      <input
        className="toolbar__name"
        value={name}
        onChange={(event) => setName(event.target.value)}
        aria-label="Flow name"
      />
      <label className="toolbar__entry">
        Entry
        <select value={entry ?? ""} onChange={(event) => setEntry(event.target.value)}>
          <option value="" disabled>
            Select entry node
          </option>
          {nodes.map((node) => (
            <option key={node.id} value={node.id}>
              {node.data.label} ({node.id})
            </option>
          ))}
        </select>
      </label>
      <button
        type="button"
        disabled
        title="Runs once the Run Manager exists (Phase 1, part B)"
      >
        Run
      </button>
    </header>
  );
}
