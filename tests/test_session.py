from unittest.mock import MagicMock

from chat.cost_tracker import CostTracker
from chat.session import ChatSession
from providers.base import ChatResult, LLMProvider, ProviderError, Usage


def _make_provider(result: ChatResult | Exception) -> MagicMock:
    provider = MagicMock(spec=LLMProvider)
    provider.name = "mock"
    provider.model = "mock-model"
    if isinstance(result, Exception):
        provider.stream_chat.side_effect = result
    else:
        provider.stream_chat.return_value = result
    return provider


class TestChatSession:
    def test_successful_turn_appends_user_and_assistant(self, chat_result: ChatResult) -> None:
        provider = _make_provider(chat_result)
        tracker = CostTracker(provider_name="groq")
        session = ChatSession(provider=provider, cost_tracker=tracker)

        session.chat("hi")

        assert len(session.messages) == 2
        assert session.messages[0] == {"role": "user", "content": "hi"}
        assert session.messages[1] == {"role": "assistant", "content": "hello"}
        assert tracker.message_count == 1
        assert tracker.total_input_tokens == 100
        assert tracker.total_output_tokens == 50

    def test_system_prompt_is_forwarded(self, chat_result: ChatResult) -> None:
        provider = _make_provider(chat_result)
        tracker = CostTracker(provider_name="groq")
        session = ChatSession(
            provider=provider, cost_tracker=tracker, system_prompt="be terse"
        )

        session.chat("hi")

        args = provider.stream_chat.call_args.args
        assert args[1] == "be terse"

    def test_provider_error_rolls_back_user_message(self) -> None:
        provider = _make_provider(ProviderError("boom"))
        tracker = CostTracker(provider_name="groq")
        session = ChatSession(provider=provider, cost_tracker=tracker)

        session.chat("hi")

        assert session.messages == []
        assert tracker.message_count == 0

    def test_clear_resets_history(self, chat_result: ChatResult) -> None:
        provider = _make_provider(chat_result)
        tracker = CostTracker(provider_name="groq")
        session = ChatSession(provider=provider, cost_tracker=tracker)
        session.chat("hi")
        assert len(session.messages) == 2

        session.clear()

        assert session.messages == []

    def test_multi_turn_history_accumulates(self) -> None:
        results = [
            ChatResult(text="first", usage=Usage(input_tokens=10, output_tokens=5)),
            ChatResult(text="second", usage=Usage(input_tokens=20, output_tokens=8)),
        ]
        provider = MagicMock(spec=LLMProvider)
        provider.name = "mock"
        provider.model = "mock-model"
        provider.stream_chat.side_effect = results

        tracker = CostTracker(provider_name="groq")
        session = ChatSession(provider=provider, cost_tracker=tracker)

        session.chat("q1")
        session.chat("q2")

        assert len(session.messages) == 4
        assert tracker.total_input_tokens == 30
        assert tracker.total_output_tokens == 13
        assert tracker.message_count == 2
