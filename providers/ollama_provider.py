import json
import requests
from providers.base import LLMProvider, ChatResult, Usage, ProviderError
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

    def stream_chat(self, messages: list[dict], system_prompt: str = "") -> ChatResult:
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        full_response = ""
        input_tokens = 0
        output_tokens = 0

        try:
            with requests.post(
                OLLAMA_URL,
                json={
                    "model": self._model,
                    "messages": all_messages,
                    "stream": True,
                },
                stream=True,
                timeout=(5, None),
            ) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if not line:
                        continue
                    data = json.loads(line)
                    chunk = data.get("message", {}).get("content", "")
                    if chunk:
                        print(chunk, end="", flush=True)
                        full_response += chunk
                    if data.get("done"):
                        input_tokens = data.get("prompt_eval_count", 0)
                        output_tokens = data.get("eval_count", 0)

            print()
            return ChatResult(
                text=full_response,
                usage=Usage(input_tokens=input_tokens, output_tokens=output_tokens),
            )

        except requests.exceptions.ConnectionError as e:
            raise ProviderError(
                "Ollama is not running. Run 'ollama serve' in the terminal."
            ) from e
        except requests.exceptions.HTTPError as e:
            raise ProviderError(f"Ollama HTTP error: {e}") from e
        except requests.exceptions.Timeout as e:
            raise ProviderError("Ollama timed out.") from e
        except (json.JSONDecodeError, KeyError) as e:
            raise ProviderError(f"Ollama returned malformed response: {e}") from e
