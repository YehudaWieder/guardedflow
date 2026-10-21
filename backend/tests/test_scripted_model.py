from app.core.llm.scripted_model import ScriptedChatModel


async def test_returns_canned_responses_in_order() -> None:
    model = ScriptedChatModel(["first", "second"])

    assert (
        await model.complete(system_prompt="", user_message="a", temperature=0.2, max_tokens=10)
        == "first"
    )
    assert (
        await model.complete(system_prompt="", user_message="b", temperature=0.2, max_tokens=10)
        == "second"
    )


async def test_echoes_once_responses_are_exhausted() -> None:
    model = ScriptedChatModel(["only"])
    await model.complete(system_prompt="", user_message="a", temperature=0.2, max_tokens=10)

    result = await model.complete(
        system_prompt="", user_message="hello", temperature=0.2, max_tokens=10
    )

    assert "hello" in result
