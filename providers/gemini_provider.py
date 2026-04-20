from google import genai
from google.genai import errors as genai_errors
from config import GEMINI_API_KEY, MODELS
from providers.base import LLMProvider, ChatResult, Usage, ProviderError


class GeminiProvider(LLMProvider):

    def __init__(self):
        if not GEMINI_API_KEY:
            raise ProviderError("GEMINI_API_KEY is missing. Set it in .env")
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self._model = MODELS["gemini"]

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def model(self) -> str:
        return self._model

    def stream_chat(self, messages: list[dict], system_prompt: str = "") -> ChatResult:
        history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [{"text": msg["content"]}]})

        last_message = messages[-1]["content"]
        all_contents = history + [{"role": "user", "parts": [{"text": last_message}]}]
        config = {"system_instruction": system_prompt} if system_prompt else None

        try:
            stream = self.client.models.generate_content_stream(
                model=self._model,
                contents=all_contents,
                config=config,
            )

            full_response = ""
            usage_meta = None

            for chunk in stream:
                text = chunk.text or ""
                print(text, end="", flush=True)
                full_response += text
                if chunk.usage_metadata is not None:
                    usage_meta = chunk.usage_metadata

            print()
            input_tokens = getattr(usage_meta, "prompt_token_count", 0) or 0
            output_tokens = getattr(usage_meta, "candidates_token_count", 0) or 0

            return ChatResult(
                text=full_response,
                usage=Usage(input_tokens=input_tokens, output_tokens=output_tokens),
            )

        except genai_errors.ClientError as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                raise ProviderError(
                    "Gemini: Quota exceeded. Wait a few minutes or use --provider groq"
                ) from e
            if "404" in str(e):
                raise ProviderError(
                    "Gemini: Model not found. Check config.py -> MODELS['gemini']"
                ) from e
            raise ProviderError(f"Gemini error: {e}") from e
        except genai_errors.ServerError as e:
            raise ProviderError(f"Gemini server error: {e}") from e
        except genai_errors.APIError as e:
            raise ProviderError(f"Gemini API error: {e}") from e
