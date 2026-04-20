from google import genai
from google.genai import errors as genai_errors
from config import GEMINI_API_KEY, MODELS
from providers.base import LLMProvider

class GeminiProvider(LLMProvider):

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self._model = MODELS["gemini"]

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def model(self) -> str:
        return self._model

    def stream_chat(self, messages: list[dict], system_prompt: str = "") -> str:
        history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [{"text": msg["content"]}]})

        last_message = messages[-1]["content"]
        all_contents = history + [{"role": "user", "parts": [{"text": last_message}]}]

        config = {"system_instruction": system_prompt} if system_prompt else {}

        try:
            response = self.client.models.generate_content(
                model=self._model,
                contents=all_contents,
                config=config if config else None,
            )
            result = response.text or ""
            print(result)
            return result

        except genai_errors.ClientError as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                msg = "[Gemini: Quota exceeded. Wait a few minutes or use --provider groq]"
            elif "404" in str(e):
                msg = "[Gemini: Model not found. Check config.py -> MODELS['gemini']]"
            else:
                msg = f"[Gemini error: {e}]"
            print(msg)
            return msg