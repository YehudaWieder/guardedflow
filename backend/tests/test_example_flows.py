"""Every fixture flow in examples/flows/ must load as a valid GraphDocument.

These fixtures are the shared basis for snapshot, equivalence, and attack
tests from Phase 1 onward.
"""

from pathlib import Path

import pytest

from app.core.schemas import GraphDocument

EXAMPLE_FLOWS_DIR = Path(__file__).parents[2] / "examples" / "flows"
EXAMPLE_FLOW_PATHS = sorted(EXAMPLE_FLOWS_DIR.glob("*.json"))


@pytest.mark.parametrize("path", EXAMPLE_FLOW_PATHS, ids=lambda p: p.stem)
def test_example_flow_loads_as_graph_document(path: Path) -> None:
    graph = GraphDocument.model_validate_json(path.read_text())
    node_ids = {node.id for node in graph.nodes}
    assert graph.entry in node_ids


def test_example_flows_dir_is_not_empty() -> None:
    assert EXAMPLE_FLOW_PATHS, f"no fixture flows found in {EXAMPLE_FLOWS_DIR}"
