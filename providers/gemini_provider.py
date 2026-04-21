import logging

from google import genai
from google.genai import errors as genai_errors
from google.genai.types import (
    ContentDict,
    GenerateContentConfigDict,
    GenerateContentResponseUsageMetadata,
)

from config import GEMINI_API_KEY, MODELS
from providers.base import ChatResult, LLMProvider, ProviderError, Usage

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    def __init__(self) -> None:
        if not GEMINI_API_KEY:
            raise ProviderError("GEMINI_API_KEY is missing. Set it in .env")
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self._model: str = MODELS["gemini"]

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def model(self) -> str:
        return self._model

    def stream_chat(
        self, messages: list[dict[str, str]], system_prompt: str = ""
    ) -> ChatResult:
        history: list[ContentDict] = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [{"text": msg["content"]}]})

        last_message = messages[-1]["content"]
        all_contents: list[ContentDict] = [
            *history,
            {"role": "user", "parts": [{"text": last_message}]},
        ]
        config: GenerateContentConfigDict | None = (
            {"system_instruction": system_prompt} if system_prompt else None
        )

        try:
            stream = self.client.models.generate_content_stream(
                model=self._model,
                contents=all_contents,
                config=config,
            )

            full_response = ""
            usage_meta: GenerateContentResponseUsageMetadata | None = None

            for chunk in stream:
                text = chunk.text or ""
                print(text, end="", flush=True)
                full_response += text
                if chunk.usage_metadata is not None:
                    usage_meta = chunk.usage_metadata

            print()
            input_tokens = 0
            output_tokens = 0
            if usage_meta is not None:
                input_tokens = usage_meta.prompt_token_count or 0
                output_tokens = usage_meta.candidates_token_count or 0

            return ChatResult(
                text=full_response,
                usage=Usage(input_tokens=input_tokens, output_tokens=output_tokens),
            )

        except genai_errors.ClientError as e:
            logger.debug("Gemini client error", exc_info=True)
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
            logger.debug("Gemini server error", exc_info=True)
            raise ProviderError(f"Gemini server error: {e}") from e
        except genai_errors.APIError as e:
            logger.debug("Gemini API error", exc_info=True)
            raise ProviderError(f"Gemini API error: {e}") from e
