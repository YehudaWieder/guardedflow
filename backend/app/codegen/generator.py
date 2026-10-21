"""Turns a normalized IRGraph into generated project files: state.py,
nodes.py, graph.py, and flow_config.json. Same IR in, byte-identical files
out — every dict/set-derived ordering is sorted before rendering.
"""

import ast
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.codegen.emitters import EMITTERS
from app.core.ir import IRGraph

_TEMPLATES_DIR = Path(__file__).parent / "templates"
_ENV = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR),
    autoescape=select_autoescape(enabled_extensions=()),
    trim_blocks=True,
    lstrip_blocks=True,
)


@dataclass(frozen=True)
class GeneratedProject:
    files: dict[str, str]


def generate_project(ir: IRGraph) -> GeneratedProject:
    return GeneratedProject(
        files={
            "state.py": _format_python(_ENV.get_template("state.py.jinja").render(name=ir.name)),
            "nodes.py": _format_python(_render_nodes(ir)),
            "graph.py": _format_python(_render_graph(ir)),
            "flow_config.json": json.dumps(_flow_config(ir), indent=2, sort_keys=True),
        }
    )


def _render_nodes(ir: IRGraph) -> str:
    names_by_module: dict[str, set[str]] = {}
    for node in ir.nodes:
        for module, name in EMITTERS[node.type].imports():
            names_by_module.setdefault(module, set()).add(name)
    imports = [
        f"from {module} import {', '.join(sorted(names))}"
        for module, names in sorted(names_by_module.items())
    ]
    function_bodies = [EMITTERS[node.type].render(node) for node in ir.nodes]
    return _ENV.get_template("nodes.py.jinja").render(
        name=ir.name, imports=imports, function_bodies=function_bodies
    )


def _render_graph(ir: IRGraph) -> str:
    node_ids = [node.id for node in ir.nodes]
    sources = {edge.source for edge in ir.edges}
    sink_ids = sorted(node_id for node_id in node_ids if node_id not in sources)
    return _ENV.get_template("graph.py.jinja").render(
        name=ir.name,
        node_ids=node_ids,
        entry=ir.entry,
        edges=ir.edges,
        sink_ids=sink_ids,
    )


def _flow_config(ir: IRGraph) -> dict[str, dict[str, Any]]:
    config: dict[str, dict[str, Any]] = {}
    for node in ir.nodes:
        if node.type == "agent":
            config[node.id] = {
                "type": "agent",
                "model": node.model,
                "system_prompt": node.system_prompt,
                "input_template": node.input_template,
                "temperature": node.temperature,
                "max_tokens": node.max_tokens,
                "tool_policy_id": node.tool_policy_id,
                "output_schema": node.output_schema,
            }
        else:
            config[node.id] = {
                "type": "mcp_tool",
                "server_id": node.server_id,
                "tool_name": node.tool_name,
                "arguments": node.arguments,
                "tool_policy_id": node.tool_policy_id,
            }
    return config


def _format_python(source: str) -> str:
    ast.parse(source)  # fail fast on a template bug before shelling out
    formatted = subprocess.run(
        ["ruff", "format", "-"],
        input=source,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    subprocess.run(
        ["ruff", "check", "-"],
        input=formatted,
        capture_output=True,
        text=True,
        check=True,
    )
    return formatted
