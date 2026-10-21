"""Validates a GraphDocument and normalizes it into the IR the codegen and
Run Manager consume: nodes in a deterministic topological order, with every
input reference checked against that order.
"""

import heapq
from collections.abc import Sequence
from dataclasses import dataclass

from app.core.errors import (
    CyclicGraphError,
    DanglingEdgeError,
    ForwardReferenceError,
    UnknownEntryError,
    UnknownReferenceError,
    UnsupportedNodeTypeError,
)
from app.core.ir.resolver import referenced_node_ids
from app.core.schemas import AgentNode, Edge, GraphDocument, MCPToolNode

SupportedNode = AgentNode | MCPToolNode


@dataclass(frozen=True)
class IRGraph:
    name: str
    entry: str
    nodes: list[SupportedNode]
    edges: list[Edge]


def normalize_graph(doc: GraphDocument) -> IRGraph:
    node_by_id = {node.id: node for node in doc.nodes}

    if doc.entry not in node_by_id:
        raise UnknownEntryError(doc.entry)

    for edge in doc.edges:
        if edge.source not in node_by_id:
            raise DanglingEdgeError(edge.id, edge.source)
        if edge.target not in node_by_id:
            raise DanglingEdgeError(edge.id, edge.target)

    supported_nodes: list[SupportedNode] = []
    for node in doc.nodes:
        if node.type not in ("agent", "mcp_tool"):
            raise UnsupportedNodeTypeError(node.id, node.type)
        supported_nodes.append(node)

    order = _topological_order(supported_nodes, doc.edges)
    order_index = {node_id: index for index, node_id in enumerate(order)}

    for node in supported_nodes:
        for referenced_id in _node_references(node):
            if referenced_id not in node_by_id:
                raise UnknownReferenceError(node.id, referenced_id)
            if order_index[referenced_id] >= order_index[node.id]:
                raise ForwardReferenceError(node.id, referenced_id)

    nodes_by_order = sorted(supported_nodes, key=lambda node: order_index[node.id])
    return IRGraph(name=doc.name, entry=doc.entry, nodes=nodes_by_order, edges=list(doc.edges))


def _node_references(node: SupportedNode) -> set[str]:
    if node.type == "agent":
        return referenced_node_ids(node.input_template)
    return {ref for value in node.arguments.values() for ref in referenced_node_ids(value)}


def _topological_order(nodes: Sequence[SupportedNode], edges: Sequence[Edge]) -> list[str]:
    in_degree = {node.id: 0 for node in nodes}
    successors: dict[str, list[str]] = {node.id: [] for node in nodes}
    for edge in edges:
        successors[edge.source].append(edge.target)
        in_degree[edge.target] += 1

    ready = sorted(node_id for node_id, degree in in_degree.items() if degree == 0)
    heapq.heapify(ready)

    order: list[str] = []
    while ready:
        current = heapq.heappop(ready)
        order.append(current)
        for successor in sorted(successors[current]):
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                heapq.heappush(ready, successor)

    if len(order) != len(nodes):
        unreached = [node.id for node in nodes if node.id not in order]
        raise CyclicGraphError(unreached)

    return order
