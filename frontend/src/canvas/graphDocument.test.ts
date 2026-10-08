import { describe, expect, it } from "vitest";

import type { GraphDocument } from "../generated/GraphDocument";
import { fromGraphDocument, toGraphDocument, UnsupportedNodeTypeError } from "./graphDocument";

const EXAMPLE: GraphDocument = {
  schema_version: 1,
  name: "linear_draft_and_send",
  entry: "draft_reply",
  policies: [
    {
      id: "support_tools",
      grants: [
        {
          server_id: "support_mcp",
          tool: "send_email",
          schema_hash: "sha256:placeholder",
          approval: "on_risk",
          arg_rules: [],
          max_calls_per_run: 3,
        },
      ],
    },
  ],
  nodes: [
    {
      type: "agent",
      id: "draft_reply",
      label: "Draft Reply",
      position: { x: 0, y: 0 },
      model: "gpt-4o-mini",
      system_prompt: "Draft a reply.",
      input_template: "Draft a reply to the customer.",
      temperature: 0.2,
      max_tokens: 512,
    },
    {
      type: "mcp_tool",
      id: "send_reply",
      label: "Send Reply",
      position: { x: 300, y: 0 },
      server_id: "support_mcp",
      tool_name: "send_email",
      arguments: { to: "customer@example.com", body: "{{outputs.draft_reply.text}}" },
      tool_policy_id: "support_tools",
    },
  ],
  edges: [{ id: "draft_reply__send_reply", source: "draft_reply", target: "send_reply" }],
};

describe("fromGraphDocument / toGraphDocument", () => {
  it("round-trips a GraphDocument through canvas state", () => {
    const { meta, nodes, edges } = fromGraphDocument(EXAMPLE);
    const roundTripped = toGraphDocument(meta, nodes, edges);
    expect(roundTripped).toEqual(EXAMPLE);
  });

  it("keeps node data separate from id/position/type", () => {
    const { nodes } = fromGraphDocument(EXAMPLE);
    const agentNode = nodes.find((n) => n.id === "draft_reply");
    expect(agentNode?.type).toBe("agent");
    expect(agentNode?.position).toEqual({ x: 0, y: 0 });
    expect(agentNode?.data).not.toHaveProperty("id");
    expect(agentNode?.data).not.toHaveProperty("position");
  });

  it("rejects node types the canvas doesn't support yet", () => {
    const withRouter: GraphDocument = {
      ...EXAMPLE,
      nodes: [
        {
          type: "router",
          id: "route",
          label: "Route",
          position: { x: 0, y: 0 },
          routes: [],
          default_target: "draft_reply",
        },
        ...EXAMPLE.nodes,
      ],
    };
    expect(() => fromGraphDocument(withRouter)).toThrow(UnsupportedNodeTypeError);
  });
});
