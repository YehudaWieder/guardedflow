from pathlib import Path

from app.codegen.generator import generate_project
from app.core.ir import normalize_graph
from app.core.schemas import GraphDocument

EXAMPLE_FLOWS_DIR = Path(__file__).parents[2] / "examples" / "flows"


def _linear_ir():
    doc = GraphDocument.model_validate_json(
        (EXAMPLE_FLOWS_DIR / "linear_draft_and_send.json").read_text()
    )
    return normalize_graph(doc)


def test_generates_one_function_per_node_in_order() -> None:
    project = generate_project(_linear_ir())

    assert "async def draft_reply(state: FlowState)" in project.files["nodes.py"]
    assert "async def send_reply(state: FlowState)" in project.files["nodes.py"]
    assert project.files["nodes.py"].index("def draft_reply") < project.files["nodes.py"].index(
        "def send_reply"
    )


def test_graph_wires_entry_and_sink_to_start_and_end() -> None:
    graph_py = generate_project(_linear_ir()).files["graph.py"]

    assert 'graph.add_edge(START, "draft_reply")' in graph_py
    assert 'graph.add_edge("draft_reply", "send_reply")' in graph_py
    assert 'graph.add_edge("send_reply", END)' in graph_py


def test_flow_config_holds_user_strings_the_generated_code_does_not() -> None:
    project = generate_project(_linear_ir())

    assert "Draft a reply" not in project.files["nodes.py"]
    assert "Draft a reply" not in project.files["graph.py"]
    assert "Draft a reply" in project.files["flow_config.json"]


def test_generation_is_deterministic() -> None:
    ir = _linear_ir()
    first = generate_project(ir)
    second = generate_project(ir)

    assert first.files == second.files
