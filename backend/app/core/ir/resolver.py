"""Finds `{{outputs.<node_id>.<field>}}` references in a template string.

No `eval`: this is pure pattern matching, used both by the IR (to check a
reference points at an earlier node) and by codegen (to emit a lookup).
"""

import re

_REFERENCE_PATTERN = re.compile(
    r"\{\{\s*outputs\.([a-z][a-z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}"
)


def referenced_node_ids(template: str) -> set[str]:
    return {match.group(1) for match in _REFERENCE_PATTERN.finditer(template)}


def resolve(template: str, outputs: dict[str, dict[str, object]]) -> str:
    """Substitutes every `{{outputs.x.y}}` in template with its value.

    Raises KeyError if a reference doesn't resolve — the IR validates every
    reference at compile time, so this should never fire against a graph
    that passed `normalize_graph`.
    """

    def _replace(match: re.Match[str]) -> str:
        node_id, field = match.group(1), match.group(2)
        return str(outputs[node_id][field])

    return _REFERENCE_PATTERN.sub(_replace, template)
