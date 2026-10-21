"""Risk derivation from MCP tool annotations. Annotations are server-supplied
hints: they can only raise the derived risk, never lower it. A server
marking a destructive tool "read-only" doesn't make it safe, and a tool
with no annotations at all is treated as risky, not trusted by default.
"""

from dataclasses import dataclass
from typing import Literal

Risk = Literal["low", "high"]


@dataclass(frozen=True)
class ToolAnnotations:
    read_only_hint: bool | None = None
    destructive_hint: bool | None = None
    open_world_hint: bool | None = None


def derive_risk(annotations: ToolAnnotations | None) -> Risk:
    if annotations is None:
        return "high"
    if annotations.destructive_hint:
        return "high"
    if annotations.open_world_hint:
        return "high"
    if annotations.read_only_hint is True:
        return "low"
    return "high"
