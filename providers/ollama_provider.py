import requests
from providers.base import LLMProvider
from config import MODELS

OLLAMA_URL = "http://localhost:11434/api/chat"

class OllamaProvider(LLMProvider):

    def __init__(self):
        self._model = MODELS["ollama"]

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def model(self) -> str:
        return self._model

    def stream_chat(self, messages: list[dict], system_prompt: str = "") -> str:
        all_messages = []

        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})

        all_messages.extend(messages)

        try:
            response = requests.post(OLLAMA_URL, json={
                "model": self._model,
                "messages": all_messages,
                "stream": False,
            })
            response.raise_for_status()
            result = response.json()["message"]["content"]
            print(result)
            return result
        except requests.exceptions.ConnectionError:
            msg = "[Ollama is not running. Run 'ollama serve' in the terminal.]"
            print(msg)
            return msg