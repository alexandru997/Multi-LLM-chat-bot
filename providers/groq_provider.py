from groq import Groq, GroqError
from config import GROQ_API_KEY, MODELS
from providers.base import LLMProvider, ChatResult, Usage, ProviderError


class GroqProvider(LLMProvider):

    def __init__(self):
        if not GROQ_API_KEY:
            raise ProviderError("GROQ_API_KEY is missing. Set it in .env")
        self.client = Groq(api_key=GROQ_API_KEY)
        self._model = MODELS["groq"]

    @property
    def name(self) -> str:
        return "groq"

    @property
    def model(self) -> str:
        return self._model

    def stream_chat(self, messages: list[dict], system_prompt: str = "") -> ChatResult:
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        try:
            stream = self.client.chat.completions.create(
                model=self._model,
                messages=all_messages,
                stream=True,
            )

            full_response = ""
            input_tokens = 0
            output_tokens = 0

            for chunk in stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta.content or ""
                    print(delta, end="", flush=True)
                    full_response += delta

                usage = getattr(getattr(chunk, "x_groq", None), "usage", None) or chunk.usage
                if usage:
                    input_tokens = usage.prompt_tokens
                    output_tokens = usage.completion_tokens

            print()
            return ChatResult(
                text=full_response,
                usage=Usage(input_tokens=input_tokens, output_tokens=output_tokens),
            )

        except GroqError as e:
            raise ProviderError(f"Groq error: {e}") from e
