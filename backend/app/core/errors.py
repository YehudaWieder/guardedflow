"""Domain errors, mapped to HTTP responses in exactly one place (the API's
exception handler, added once routes exist). Modules raise these; nothing
in `core` or `runs` catches and reinterprets them.
"""


class GuardedFlowError(Exception):
    """Base for every domain error in the app."""


class IRError(GuardedFlowError):
    """A GraphDocument doesn't normalize to a runnable IR."""


class UnknownEntryError(IRError):
    def __init__(self, entry: str) -> None:
        super().__init__(f"entry {entry!r} does not match any node id")


class DanglingEdgeError(IRError):
    def __init__(self, edge_id: str, missing_node_id: str) -> None:
        super().__init__(f"edge {edge_id!r} references unknown node {missing_node_id!r}")


class UnsupportedNodeTypeError(IRError):
    def __init__(self, node_id: str, node_type: str) -> None:
        super().__init__(f"node {node_id!r} has type {node_type!r}, not supported by the IR yet")


class CyclicGraphError(IRError):
    def __init__(self, unreachable_node_ids: list[str]) -> None:
        super().__init__(f"graph has a cycle involving: {', '.join(sorted(unreachable_node_ids))}")


class UnknownReferenceError(IRError):
    def __init__(self, node_id: str, referenced_node_id: str) -> None:
        super().__init__(f"node {node_id!r} references unknown node {referenced_node_id!r}")


class ForwardReferenceError(IRError):
    def __init__(self, node_id: str, referenced_node_id: str) -> None:
        super().__init__(
            f"node {node_id!r} references {referenced_node_id!r}, "
            "which does not come before it in the graph"
        )
