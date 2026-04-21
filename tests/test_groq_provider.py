from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from groq import GroqError
from pytest_mock import MockerFixture

from providers.base import ProviderError


def _chunk(content: str = "", usage: object | None = None) -> SimpleNamespace:
    delta = SimpleNamespace(content=content)
    choice = SimpleNamespace(delta=delta)
    return SimpleNamespace(choices=[choice], x_groq=None, usage=usage)


class TestGroqProvider:
    def test_missing_api_key_raises_provider_error(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch("providers.groq_provider.GROQ_API_KEY", None)

        from providers.groq_provider import GroqProvider

        with pytest.raises(ProviderError, match="GROQ_API_KEY"):
            GroqProvider()

    def test_stream_chat_accumulates_text_and_usage(
        self, mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
    ) -> None:
        mocker.patch("providers.groq_provider.GROQ_API_KEY", "fake-key")
        groq_cls = mocker.patch("providers.groq_provider.Groq")

        usage_obj = SimpleNamespace(prompt_tokens=42, completion_tokens=17)
        fake_stream = [
            _chunk(content="hel"),
            _chunk(content="lo"),
            _chunk(content="", usage=usage_obj),
        ]
        client = MagicMock()
        client.chat.completions.create.return_value = iter(fake_stream)
        groq_cls.return_value = client

        from providers.groq_provider import GroqProvider

        provider = GroqProvider()
        result = provider.stream_chat([{"role": "user", "content": "hi"}])

        assert result.text == "hello"
        assert result.usage.input_tokens == 42
        assert result.usage.output_tokens == 17

        captured = capsys.readouterr()
        assert "hello" in captured.out

    def test_system_prompt_is_prepended(self, mocker: MockerFixture) -> None:
        mocker.patch("providers.groq_provider.GROQ_API_KEY", "fake-key")
        groq_cls = mocker.patch("providers.groq_provider.Groq")

        client = MagicMock()
        client.chat.completions.create.return_value = iter([_chunk(content="ok")])
        groq_cls.return_value = client

        from providers.groq_provider import GroqProvider

        provider = GroqProvider()
        provider.stream_chat(
            [{"role": "user", "content": "hi"}], system_prompt="be brief"
        )

        sent = client.chat.completions.create.call_args.kwargs["messages"]
        assert sent[0] == {"role": "system", "content": "be brief"}
        assert sent[1] == {"role": "user", "content": "hi"}

    def test_groq_error_wrapped_as_provider_error(self, mocker: MockerFixture) -> None:
        mocker.patch("providers.groq_provider.GROQ_API_KEY", "fake-key")
        groq_cls = mocker.patch("providers.groq_provider.Groq")

        client = MagicMock()
        client.chat.completions.create.side_effect = GroqError("rate limited")
        groq_cls.return_value = client

        from providers.groq_provider import GroqProvider

        provider = GroqProvider()
        with pytest.raises(ProviderError, match="Groq error"):
            provider.stream_chat([{"role": "user", "content": "hi"}])

    def test_name_and_model_properties(self, mocker: MockerFixture) -> None:
        mocker.patch("providers.groq_provider.GROQ_API_KEY", "fake-key")
        mocker.patch("providers.groq_provider.Groq")

        from providers.groq_provider import GroqProvider

        provider = GroqProvider()
        assert provider.name == "groq"
        assert provider.model  # non-empty
