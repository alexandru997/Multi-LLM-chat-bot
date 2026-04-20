from groq import Groq
from config import GROQ_API_KEY, MODELS
from providers.base import LLMProvider

class GroqProvider(LLMProvider):

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self._model = MODELS["groq"]

    @property
    def name(self) -> str:
        return "groq"

    @property
    def model(self) -> str:
        return self._model

    def stream_chat(self, messages: list[dict], system_prompt: str = "") -> str:
        all_messages = []

        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})

        all_messages.extend(messages)

        stream = self.client.chat.completions.create(
            model=self._model,
            messages=all_messages,
            stream=True,
        )

        full_response = ""
        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            print(delta, end="", flush=True)
            full_response += delta

        print()
        return full_response