from abc import ABC, abstractmethod
from dataclasses import dataclass


class ProviderError(Exception):
    """Raised when a provider fails to produce a response."""


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class ChatResult:
    text: str
    usage: Usage


class LLMProvider(ABC):
    """Contract every LLM backend must implement.

    Implementations are expected to stream output to stdout as it arrives
    and return the full response text along with real token usage.
    On failure they raise ProviderError with a user-facing message.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier used on the CLI (e.g. 'groq')."""

    @property
    @abstractmethod
    def model(self) -> str:
        """Model ID currently in use for this provider."""

    @abstractmethod
    def stream_chat(self, messages: list[dict], system_prompt: str = "") -> ChatResult:
        """Send a chat turn, stream output, and return (text, usage).

        Raises ProviderError on any failure (network, quota, bad model, ...).
        """
