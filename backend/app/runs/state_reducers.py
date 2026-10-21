"""Reducers for FlowState keys that need merge-not-replace semantics across
node updates. `messages` already gets this from LangGraph's `add_messages`;
`outputs` needs the same so each node can write only its own key.
"""

from typing import Any


def merge_outputs(
    current: dict[str, dict[str, Any]], update: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    return {**current, **update}
