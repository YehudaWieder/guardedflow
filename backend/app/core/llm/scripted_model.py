"""The ChatModelPort implementation wired in until a real provider's API key
is configured. Given canned responses, returns them in order — useful for
both manual runs and deterministic tests; otherwise echoes a placeholder.
"""


class ScriptedChatModel:
    def __init__(self, responses: list[str] | None = None) -> None:
        self._responses = responses or []
        self._next = 0

    async def complete(
        self,
        *,
        system_prompt: str,
        user_message: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        if self._next < len(self._responses):
            response = self._responses[self._next]
            self._next += 1
            return response
        return f"[scripted: no provider configured] {user_message[:200]}"
