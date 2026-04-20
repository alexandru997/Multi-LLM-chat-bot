from providers.base import LLMProvider, ProviderError, ChatResult, Usage
from providers.groq_provider import GroqProvider
from providers.gemini_provider import GeminiProvider
from providers.ollama_provider import OllamaProvider

PROVIDER_MAP = {
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
