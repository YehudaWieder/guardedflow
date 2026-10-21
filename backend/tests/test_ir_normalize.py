from pathlib import Path

import pytest

from app.core.errors import (
    CyclicGraphError,
    DanglingEdgeError,
    ForwardReferenceError,
    UnknownEntryError,
    UnknownReferenceError,
    UnsupportedNodeTypeError,
)
from app.core.ir import normalize_graph
from app.core.schemas import GraphDocument

EXAMPLE_FLOWS_DIR = Path(__file__).parents[2] / "examples" / "flows"


def test_normalizes_the_linear_fixture_in_edge_order() -> None:
    doc = GraphDocument.model_validate_json(
        (EXAMPLE_FLOWS_DIR / "linear_draft_and_send.json").read_text()
    )

    ir = normalize_graph(doc)

    assert [node.id for node in ir.nodes] == ["draft_reply", "send_reply"]
    assert ir.entry == "draft_reply"


def test_rejects_unknown_entry() -> None:
    doc = _graph_document(entry="missing", nodes=[_agent("a")], edges=[])

    with pytest.raises(UnknownEntryError):
        normalize_graph(doc)


def test_rejects_dangling_edge() -> None:
    doc = _graph_document(
        entry="a",
        nodes=[_agent("a")],
        edges=[{"id": "e1", "source": "a", "target": "missing"}],
    )

    with pytest.raises(DanglingEdgeError):
        normalize_graph(doc)


def test_rejects_unsupported_node_type() -> None:
    doc = _graph_document(
        entry="a",
        nodes=[
            _agent("a"),
            {
                "type": "router",
                "id": "r",
                "label": "Router",
                "position": {"x": 0, "y": 0},
                "routes": [],
                "default_target": "a",
            },
        ],
        edges=[],
    )

    with pytest.raises(UnsupportedNodeTypeError):
        normalize_graph(doc)


def test_rejects_cycle() -> None:
    doc = _graph_document(
        entry="a",
        nodes=[_agent("a"), _agent("b")],
        edges=[
            {"id": "e1", "source": "a", "target": "b"},
            {"id": "e2", "source": "b", "target": "a"},
        ],
    )

    with pytest.raises(CyclicGraphError):
        normalize_graph(doc)


def test_rejects_reference_to_unknown_node() -> None:
    doc = _graph_document(
        entry="a",
        nodes=[_agent("a", input_template="{{outputs.ghost.text}}")],
        edges=[],
    )

    with pytest.raises(UnknownReferenceError):
        normalize_graph(doc)


def test_rejects_forward_reference() -> None:
    doc = _graph_document(
        entry="a",
        nodes=[
            _agent("a", input_template="{{outputs.b.text}}"),
            _agent("b"),
        ],
        edges=[{"id": "e1", "source": "a", "target": "b"}],
    )

    with pytest.raises(ForwardReferenceError):
        normalize_graph(doc)


def _agent(node_id: str, input_template: str = "do the thing") -> dict[str, object]:
    return {
        "type": "agent",
        "id": node_id,
        "label": node_id,
        "position": {"x": 0, "y": 0},
        "model": "gpt-4o-mini",
        "system_prompt": "be helpful",
        "input_template": input_template,
    }


def _graph_document(
    *, entry: str, nodes: list[dict[str, object]], edges: list[dict[str, object]]
) -> GraphDocument:
    return GraphDocument.model_validate(
        {
            "schema_version": 1,
            "name": "test_flow",
            "entry": entry,
            "nodes": nodes,
            "edges": edges,
        }
    )
