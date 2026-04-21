import pytest

from providers import (
    PROVIDER_MAP,
    GeminiProvider,
    GroqProvider,
    LLMProvider,
    OllamaProvider,
    get_provider,
)


class TestProviderFactory:
    def test_map_contains_all_expected_providers(self) -> None:
        assert set(PROVIDER_MAP.keys()) == {"groq", "gemini", "ollama"}

    def test_map_values_are_llmprovider_subclasses(self) -> None:
        for cls in PROVIDER_MAP.values():
            assert issubclass(cls, LLMProvider)

    def test_ollama_factory_instantiates_without_keys(self) -> None:
        # Ollama doesn't need API keys, so the factory call should succeed here.
        provider = get_provider("ollama")
        assert isinstance(provider, OllamaProvider)
        assert provider.name == "ollama"

    def test_unknown_provider_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("claude")

    def test_map_entries_point_to_correct_classes(self) -> None:
        assert PROVIDER_MAP["groq"] is GroqProvider
        assert PROVIDER_MAP["gemini"] is GeminiProvider
        assert PROVIDER_MAP["ollama"] is OllamaProvider
