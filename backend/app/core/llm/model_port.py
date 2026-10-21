"""ChatModelPort: the one seam between the IR and an LLM provider.

The IR and codegen never import a provider SDK directly — every Agent node
call goes through this port, so swapping providers touches one class.
"""

from typing import Protocol


class ChatModelPort(Protocol):
    async def complete(
        self,
        *,
        system_prompt: str,
        user_message: str,
        temperature: float,
        max_tokens: int,
    ) -> str: ...
