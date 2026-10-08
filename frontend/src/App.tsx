import { ReactFlowProvider } from "@xyflow/react";

import { Canvas } from "./canvas/Canvas";
import "./App.css";
import { NodePropertiesPanel } from "./panels/NodePropertiesPanel";
import { Palette } from "./panels/Palette";
import { Toolbar } from "./panels/Toolbar";

export default function App() {
  return (
    <ReactFlowProvider>
      <div className="app">
        <Toolbar />
        <div className="app__body">
          <Palette />
          <div className="app__canvas">
            <Canvas />
          </div>
          <NodePropertiesPanel />
        </div>
      </div>
    </ReactFlowProvider>
  );
}
