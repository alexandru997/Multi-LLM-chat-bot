from abc import ABC, abstractmethod

class LLMProvider(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        pass

    @abstractmethod
    def stream_chat(self, messages: list[dict], system_prompt: str = "") -> str:
        pass