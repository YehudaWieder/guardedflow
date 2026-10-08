"""Exports JSON Schema for each top-level model, consumed by the frontend's
`pnpm gen:types` (json-schema-to-typescript) to produce `src/generated/*.ts`.

Usage: uv run python -m app.core.schemas.export_json_schema <output-dir>
"""

import json
import sys
from pathlib import Path

from pydantic import BaseModel, RootModel

from app.core.schemas.events import Event as EventUnion
from app.core.schemas.graph import GraphDocument
from app.core.schemas.policy import ToolPolicy


class Event(RootModel[EventUnion]):
    pass


MODELS: list[type[BaseModel]] = [GraphDocument, ToolPolicy, Event]


def main(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for model in MODELS:
        schema = model.model_json_schema()
        schema.setdefault("title", model.__name__)
        (out_dir / f"{model.__name__}.json").write_text(json.dumps(schema, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
