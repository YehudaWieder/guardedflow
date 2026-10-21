"""Writes a generated project to a real package on disk and imports it.
Generated nodes.py/graph.py use relative imports (`from . import nodes`),
so they need to live in an actual package, not be exec'd standalone.
"""

import importlib
import sys
import tempfile
from pathlib import Path
from types import ModuleType


def load_generated_graph_module(run_id: str, files: dict[str, str]) -> ModuleType:
    package_name = f"_generated_flow_{run_id}"
    base_dir = Path(tempfile.gettempdir()) / "guardedflow_runs" / package_name
    base_dir.mkdir(parents=True, exist_ok=True)
    (base_dir / "__init__.py").write_text("")
    for filename, content in files.items():
        if filename.endswith(".py"):
            (base_dir / filename).write_text(content, encoding="utf-8")

    parent_dir = str(base_dir.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    return importlib.import_module(f"{package_name}.graph")
