from providers.base import ChatResult, LLMProvider, ProviderError, Usage
from providers.gemini_provider import GeminiProvider
from providers.groq_provider import GroqProvider
from providers.ollama_provider import OllamaProvider

PROVIDER_MAP: dict[str, type[LLMProvider]] = {
    "groq": GroqProvider,
    "gemini": GeminiProvider,
    "ollama": OllamaProvider,
}


def get_provider(name: str) -> LLMProvider:
    if name not in PROVIDER_MAP:
        raise ValueError(
            f"Unknown provider: '{name}'. Choose from: {list(PROVIDER_MAP.keys())}"
        )
    return PROVIDER_MAP[name]()


__all__ = [
    "PROVIDER_MAP",
    "ChatResult",
    "GeminiProvider",
    "GroqProvider",
    "LLMProvider",
    "OllamaProvider",
    "ProviderError",
    "Usage",
    "get_provider",
]
