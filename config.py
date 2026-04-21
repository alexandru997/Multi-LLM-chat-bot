import os

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

MODELS: dict[str, str] = {
    "groq": "llama-3.3-70b-versatile",
    "gemini": "gemini-2.0-flash-lite",
    "ollama": "llama3.2",
}

PROVIDERS: list[str] = ["groq", "gemini", "ollama"]

PRICING: dict[str, dict[str, float]] = {
    "groq":   {"input": 0.59e-6, "output": 0.79e-6},
    "gemini": {"input": 0.075e-6, "output": 0.30e-6},
    "ollama": {"input": 0.0, "output": 0.0},
}
