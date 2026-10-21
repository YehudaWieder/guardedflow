"""Re-exports flowpermit's policy models for GraphDocument composition.

The canonical definition lives in flowpermit (vendored standalone into every
export); the backend depends on it, not the other way around.
"""

from flowpermit.models import ArgRule, ToolGrant, ToolPolicy

__all__ = ["ArgRule", "ToolGrant", "ToolPolicy"]
